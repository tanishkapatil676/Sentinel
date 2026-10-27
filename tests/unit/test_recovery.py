
import uuid
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select

from sentinel.database import AsyncSessionLocal
from sentinel.models.job import Job, JobStatus
from sentinel.tasks.recovery import recover_stale_jobs


def unique_job_id():
    # UUID string is exactly 36 characters.
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_stale_job_recovery_requeues():
    job_id = unique_job_id()

    async with AsyncSessionLocal() as session:
        job = Job(
            id=job_id,
            name="stale-task",
            payload="{}",
            status=JobStatus.RUNNING,
            retry_count=0,
            max_retries=3,
            updated_at=(
                datetime.now(timezone.utc) - timedelta(minutes=20)
            ),
        )

        session.add(job)
        await session.commit()

        try:
            reclaimed_count = await recover_stale_jobs(
                stale_threshold_minutes=15,
                db_session=session,
            )

            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            recovered_job = result.scalar_one()

            assert reclaimed_count >= 1
            assert recovered_job.status == JobStatus.PENDING
            assert recovered_job.retry_count == 1
            assert "Recovered from stale" in recovered_job.error_message

        finally:
            await session.execute(
                delete(Job).where(Job.id == job_id)
            )
            await session.commit()


@pytest.mark.asyncio
async def test_healthy_job_not_reclaimed():
    job_id = unique_job_id()

    async with AsyncSessionLocal() as session:
        job = Job(
            id=job_id,
            name="healthy-task",
            payload="{}",
            status=JobStatus.RUNNING,
            retry_count=0,
            max_retries=3,
            updated_at=(
                datetime.now(timezone.utc) - timedelta(minutes=2)
            ),
        )

        session.add(job)
        await session.commit()

        try:
            await recover_stale_jobs(
                stale_threshold_minutes=15,
                db_session=session,
            )

            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            healthy_job = result.scalar_one()

            assert healthy_job.status == JobStatus.RUNNING
            assert healthy_job.retry_count == 0

        finally:
            await session.execute(
                delete(Job).where(Job.id == job_id)
            )
            await session.commit()
