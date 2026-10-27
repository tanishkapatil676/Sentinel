from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from sentinel.database import AsyncSessionLocal
from sentinel.models.job import Job, JobStatus
from sentinel.tasks.jobs import _execute_job_async


@pytest.mark.asyncio
async def test_end_to_end_job_lifecycle_flow():
    """
    Tests durable job creation, direct worker execution,
    and persisted completion in the database.

    Does not test the HTTP API or real Redis dispatch.
    """
    job_id = str(uuid4())

    async with AsyncSessionLocal() as session:
        try:
            # Step 1: Create and persist the job.
            job = Job(
                id=job_id,
                name="e2e-integration-task",
                payload='{"value": 42}',
                status=JobStatus.PENDING,
                retry_count=0,
                max_retries=3,
            )
            session.add(job)
            await session.commit()

            # Step 2: Confirm durable registration.
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            stored_job = result.scalar_one()

            assert stored_job.status == JobStatus.PENDING

            # Step 3: Execute the worker logic directly.
            await _execute_job_async(job_id)

            # Step 4: Verify persisted completion.
            await session.refresh(stored_job)

            assert stored_job.status == JobStatus.COMPLETED
            assert stored_job.result is not None
            assert stored_job.error_message is None

        finally:
            await session.execute(
                delete(Job).where(Job.id == job_id)
            )
            await session.commit()
