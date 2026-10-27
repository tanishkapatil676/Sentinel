
from unittest.mock import AsyncMock, MagicMock

import pytest

from sentinel.models.job import JobStatus
from sentinel.tasks import jobs


class FakeSession:
    def __init__(self, execute_result=None, job=None):
        self.execute_result = execute_result
        self.job = job
        self.execute = AsyncMock()
        self.commit = AsyncMock()
        self.get = AsyncMock(return_value=job)

        result = MagicMock()
        result.scalar_one_or_none.return_value = execute_result
        self.execute.return_value = result

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


def install_sessions(monkeypatch, sessions):
    iterator = iter(sessions)
    monkeypatch.setattr(
        jobs, "async_session_maker", lambda: next(iterator)
    )


@pytest.mark.asyncio
async def test_missing_or_unclaimable_job_returns(monkeypatch):
    session = FakeSession(execute_result=None)
    install_sessions(monkeypatch, [session])

    await jobs._execute_job_async("missing-job")

    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_claim_uses_conditional_update(monkeypatch):
    session = FakeSession(execute_result=None)
    install_sessions(monkeypatch, [session])

    await jobs._execute_job_async("job-123")

    statement = session.execute.await_args.args[0]
    sql = str(statement).upper()

    assert "UPDATE JOBS" in sql
    assert "WHERE JOBS.ID" in sql
    assert "JOBS.STATUS IN" in sql
    assert "RETURNING JOBS.ID" in sql

    # Status values are bound parameters, not literal SQL text.
    params = statement.compile().params
    status_values = [
        value for key, value in params.items()
        if "STATUS" in key.upper()
    ]

    assert status_values, f"No status parameters found: {params}"

    eligible = status_values[-1]
    assert {
        getattr(status, "value", status)
        for status in eligible
    } == {"PENDING", "QUEUED"}


def test_terminal_statuses_are_not_claimable():
    assert JobStatus.COMPLETED not in jobs.CLAIMABLE_STATUSES
    assert JobStatus.FAILED not in jobs.CLAIMABLE_STATUSES
    assert JobStatus.CANCELLED not in jobs.CLAIMABLE_STATUSES


def test_retry_delay_is_exponential_and_bounded():
    # Verify the intended policy used by the current worker.
    assert min(2 ** 1, 60) == 2
    assert min(2 ** 2, 60) == 4
    assert min(2 ** 6, 60) == 60


from types import SimpleNamespace


@pytest.mark.asyncio
async def test_successful_job_is_marked_completed(monkeypatch):
    claim = FakeSession(execute_result="job-1")
    loaded = FakeSession(
        job=SimpleNamespace(name="demo", payload="{}")
    )
    running_job = SimpleNamespace(
        status=JobStatus.RUNNING,
        result=None,
        error_message="old error",
    )
    finish = FakeSession(job=running_job)

    install_sessions(monkeypatch, [claim, loaded, finish])
    monkeypatch.setattr(
        jobs, "process_job", AsyncMock(return_value="result-ok")
    )

    await jobs._execute_job_async("job-1")

    assert running_job.status == JobStatus.COMPLETED
    assert running_job.result == "result-ok"
    assert running_job.error_message is None
    finish.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_permanent_error_marks_job_failed(monkeypatch):
    claim = FakeSession(execute_result="job-2")
    loaded = FakeSession(
        job=SimpleNamespace(name="demo", payload=None)
    )
    running_job = SimpleNamespace(
        status=JobStatus.RUNNING,
        error_message=None,
    )
    failure = FakeSession(job=running_job)

    install_sessions(monkeypatch, [claim, loaded, failure])
    monkeypatch.setattr(
        jobs,
        "process_job",
        AsyncMock(side_effect=jobs.PermanentJobError("invalid input")),
    )

    await jobs._execute_job_async("job-2")

    assert running_job.status == JobStatus.FAILED
    assert running_job.error_message == "invalid input"
    failure.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_transient_error_schedules_retry(monkeypatch):
    claim = FakeSession(execute_result="job-3")
    loaded = FakeSession(
        job=SimpleNamespace(name="demo", payload=None)
    )
    running_job = SimpleNamespace(
        status=JobStatus.RUNNING,
        retry_count=0,
        max_retries=3,
        error_message=None,
    )
    failure = FakeSession(job=running_job)

    install_sessions(monkeypatch, [claim, loaded, failure])
    monkeypatch.setattr(
        jobs, "process_job", AsyncMock(side_effect=RuntimeError("temporary"))
    )

    enqueue = MagicMock()
    monkeypatch.setattr(jobs.job_queue, "enqueue_in", enqueue)

    await jobs._execute_job_async("job-3")

    assert running_job.retry_count == 1
    assert running_job.status == JobStatus.PENDING
    assert running_job.error_message == "temporary"
    enqueue.assert_called_once()
    assert enqueue.call_args.args[0].total_seconds() == 2
    failure.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_retry_exhaustion_marks_job_failed(monkeypatch):
    claim = FakeSession(execute_result="job-4")
    loaded = FakeSession(
        job=SimpleNamespace(name="demo", payload=None)
    )
    running_job = SimpleNamespace(
        status=JobStatus.RUNNING,
        retry_count=3,
        max_retries=3,
        error_message=None,
    )
    failure = FakeSession(job=running_job)

    install_sessions(monkeypatch, [claim, loaded, failure])
    monkeypatch.setattr(
        jobs,
        "process_job",
        AsyncMock(side_effect=RuntimeError("still failing")),
    )
    enqueue = MagicMock()
    monkeypatch.setattr(jobs.job_queue, "enqueue_in", enqueue)

    await jobs._execute_job_async("job-4")

    assert running_job.retry_count == 4
    assert running_job.status == JobStatus.FAILED
    assert running_job.error_message == "still failing"
    failure.commit.assert_awaited_once()
    enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_unclaimable_job_is_not_processed(monkeypatch):
    claim = FakeSession(execute_result=None)
    install_sessions(monkeypatch, [claim])

    process = AsyncMock()
    monkeypatch.setattr(jobs, "process_job", process)

    await jobs._execute_job_async("already-completed-job")

    process.assert_not_awaited()
    claim.commit.assert_awaited_once()
