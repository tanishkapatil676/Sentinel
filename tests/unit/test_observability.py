import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import sentinel.tasks.jobs as jobs


class FakeSession:
    def __init__(self, execute_result=None, job=None):
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


@pytest.mark.asyncio
async def test_successful_job_emits_completion_log(monkeypatch, caplog):
    job_id = "obs-job-1"

    loaded_job = SimpleNamespace(
        name="demo",
        payload='{"value": 1}',
    )

    completed_job = SimpleNamespace(
        status=jobs.JobStatus.RUNNING,
        result=None,
        error_message="old error",
    )

    sessions = iter([
        FakeSession(execute_result=job_id),  # Atomic claim
        FakeSession(job=loaded_job),         # Load job
        FakeSession(job=completed_job),      # Save completion
    ])

    monkeypatch.setattr(
        jobs,
        "async_session_maker",
        lambda: next(sessions),
    )

    monkeypatch.setattr(
        jobs,
        "process_job",
        AsyncMock(return_value="result-ok"),
    )

    with caplog.at_level(logging.INFO, logger="sentinel.tasks.jobs"):
        await jobs._execute_job_async(job_id)

    assert completed_job.status == jobs.JobStatus.COMPLETED
    assert completed_job.result == "result-ok"
    assert completed_job.error_message is None

    assert "Job obs-job-1 completed successfully." in caplog.text
