import uuid
import pytest
import asyncio
from sentinel.database import AsyncSessionLocal
from sentinel.models.job import Job, JobStatus
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_end_to_end_job_lifecycle_flow():
    """
    Verifies the end-to-end lifecycle:
    1. Durable job creation in PostgreSQL.
    2. Simulated queue dispatch & worker execution.
    3. Safe state transition to COMPLETED with persisted results.
    """
    job_id = str(uuid.uuid4())

    # Step 1: Durable registration (simulating API intake)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            job = Job(
                id=job_id,
                name="e2e-integration-task",
                payload="{\"value\": 42}",
                status=JobStatus.PENDING,
                retry_count=0,
                max_retries=3
            )
            session.add(job)
            await session.commit()

    # Step 2: Verify durable persistence
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).where(Job.id == job_id))
        persisted_job = result.scalar_one_or_none()
        assert persisted_job is not None
        assert persisted_job.status == JobStatus.PENDING

    # Step 3: Simulate worker processing & successful state transition
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Job).where(Job.id == job_id).with_for_update()
            )
            job_to_run = result.scalar_one()
            job_to_run.status = JobStatus.RUNNING
            await session.commit()

        # Simulate task execution
        await asyncio.sleep(0.1)

        async with session.begin():
            result = await session.execute(select(Job).where(Job.id == job_id))
            job_completed = result.scalar_one()
            job_completed.status = JobStatus.COMPLETED
            job_completed.result = "{\"output\": 84}"
            await session.commit()

    # Step 4: Verify final completed state and result retrieval
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).where(Job.id == job_id))
        final_job = result.scalar_one()
        assert final_job.status == JobStatus.COMPLETED
        assert final_job.result == "{\"output\": 84}"
