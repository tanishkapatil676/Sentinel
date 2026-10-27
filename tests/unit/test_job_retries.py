from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call

import pytest

import sentinel.tasks.jobs as jobs


class FakeSession:
    def __init__(self, claimed_id=None, job=None):
        self.execute = AsyncMock()
        self.commit = AsyncMock()
        self.get = AsyncMock(return_value=job)

        result = MagicMock()
        result.scalar_one_or_none.return_value = claimed_id
        self.execute.return_value = result

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_transient_failure_schedules_retry(monkeypatch):
    job_id = "retry-test-001"

    loaded_job = SimpleNamespace(
        name="transient-task",
        payload='{"value": 1}',
    )

    persisted_job = SimpleNamespace(
        status=jobs.JobStatus.RUNNING,
        retry_count=0,
        max_retries=3,
        error_message=None,
    )

    sessions = iter([
        FakeSession(claimed_id=job_id),
        FakeSession(job=loaded_job),
        FakeSession(job=persisted_job),
    ])

    monkeypatch.setattr(
        jobs,
        "async_session_maker",
        lambda: next(sessions),
    )

    monkeypatch.setattr(
        jobs,
        "process_job",
        AsyncMock(side_effect=RuntimeError("temporary failure")),
    )

    enqueue_in = MagicMock()
    monkeypatch.setattr(jobs.job_queue, "enqueue_in", enqueue_in)

    await jobs._execute_job_async(job_id)

    assert persisted_job.status == jobs.JobStatus.PENDING
    assert persisted_job.retry_count == 1
    assert persisted_job.error_message == "temporary failure"

    assert enqueue_in.call_count == 1
    args, kwargs = enqueue_in.call_args
    assert args[0].total_seconds() == 2
    assert args[1] is jobs.execute_job
    assert args[2] == job_id

    jobs.process_job.assert_awaited_once_with(
        "transient-task",
        {"value": 1},
    )


@pytest.mark.asyncio
async def test_retry_exhaustion_marks_job_failed(monkeypatch):
    job_id = "retry-test-002"

    loaded_job = SimpleNamespace(
        name="exhausted-task",
        payload="{}",
    )

    persisted_job = SimpleNamespace(
        status=jobs.JobStatus.RUNNING,
        retry_count=0,
        max_retries=0,
        error_message=None,
    )

    sessions = iter([
        FakeSession(claimed_id=job_id),
        FakeSession(job=loaded_job),
        FakeSession(job=persisted_job),
    ])

    monkeypatch.setattr(
        jobs,
        "async_session_maker",
        lambda: next(sessions),
    )

    monkeypatch.setattr(
        jobs,
        "process_job",
        AsyncMock(side_effect=RuntimeError("permanent for this test")),
    )

    enqueue_in = MagicMock()
    monkeypatch.setattr(jobs.job_queue, "enqueue_in", enqueue_in)

    await jobs._execute_job_async(job_id)

    assert persisted_job.status == jobs.JobStatus.FAILED
    assert persisted_job.retry_count == 1
    assert persisted_job.error_message == "permanent for this test"

    enqueue_in.assert_not_called()

    jobs.process_job.assert_awaited_once_with(
        "exhausted-task",
        {},
    )
