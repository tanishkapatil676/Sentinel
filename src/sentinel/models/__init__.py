from sentinel.models.job import Job, JobStatus
from sentinel.models.idempotency import IdempotencyRecord

# Backward-compatible aliases for code that imports these names.
JobModel = Job
JobState = JobStatus

__all__ = [
    "Job",
    "JobModel",
    "JobStatus",
    "JobState",
    "IdempotencyRecord",
]
