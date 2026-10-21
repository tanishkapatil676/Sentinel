import pytest

from sentinel.models.job import Job, JobStatus


@pytest.mark.unit
def test_job_model_instantiation():
    job = Job(
        id="test-job-id-123",
        name="test_task",
        status=JobStatus.PENDING,
        payload='{"key": "value"}',
    )
    assert job.id == "test-job-id-123"
    assert job.name == "test_task"
    assert job.status == JobStatus.PENDING
    assert job.payload == '{"key": "value"}'
    assert job.result is None
    assert job.error_message is None
