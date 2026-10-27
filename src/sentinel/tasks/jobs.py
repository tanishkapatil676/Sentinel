import asyncio
import logging
from datetime import timedelta

from sqlalchemy import update

from sentinel.database import async_session_maker
from sentinel.models.job import Job, JobStatus
from sentinel.queue import job_queue

logger = logging.getLogger(__name__)

CLAIMABLE_STATUSES = (JobStatus.PENDING, JobStatus.QUEUED)
TERMINAL_STATUSES = (
    JobStatus.COMPLETED,
    JobStatus.FAILED,
    JobStatus.CANCELLED,
)


class PermanentJobError(Exception):
    """An unrecoverable error that must not be retried."""


async def process_job(name: str, payload: str | None) -> str:
    """Placeholder task handler; replace with real processing logic."""
    await asyncio.sleep(0.5)
    return f"Successfully processed job {name}. Payload: {payload}"


async def _execute_job_async(job_id: str) -> None:
    # Atomic conditional update: only one worker can claim an eligible job.
    async with async_session_maker() as session:
        result = await session.execute(
            update(Job)
            .where(
                Job.id == job_id,
                Job.status.in_(CLAIMABLE_STATUSES),
            )
            .values(status=JobStatus.RUNNING)
            .returning(Job.id)
        )
        claimed_id = result.scalar_one_or_none()
        await session.commit()

    if claimed_id is None:
        logger.info(
            "Job %s is missing, already claimed, or not eligible",
            job_id,
        )
        return

    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job is None:
            logger.error("Claimed job %s disappeared", job_id)
            return
        name, payload = job.name, job.payload

    try:
        result_value = await process_job(name, payload)

    except PermanentJobError as exc:
        async with async_session_maker() as session:
            job = await session.get(Job, job_id)
            if job is not None and job.status == JobStatus.RUNNING:
                job.status = JobStatus.FAILED
                job.error_message = str(exc)
                await session.commit()
        logger.error("Job %s failed permanently: %s", job_id, exc)
        return

    except Exception as exc:
        retry_delay = None
        retry_count = 0
        max_retries = 0

        async with async_session_maker() as session:
            job = await session.get(Job, job_id)
            if job is None or job.status != JobStatus.RUNNING:
                logger.warning("Job %s changed state during failure handling", job_id)
                return

            job.retry_count += 1
            retry_count = job.retry_count
            max_retries = job.max_retries
            job.error_message = str(exc)

            if retry_count <= max_retries:
                retry_delay = min(2 ** retry_count, 60)
                job.status = JobStatus.PENDING
            else:
                job.status = JobStatus.FAILED

            await session.commit()

        if retry_delay is None:
            logger.error(
                "Job %s exhausted retries (%s/%s)",
                job_id, retry_count, max_retries,
            )
            return

        try:
            job_queue.enqueue_in(
                timedelta(seconds=retry_delay),
                execute_job,
                job_id,
            )
            logger.warning(
                "Retry %s/%s scheduled for job %s in %s seconds",
                retry_count, max_retries, job_id, retry_delay,
            )
        except Exception:
            # A durable outbox/reconciler is still needed for guaranteed recovery.
            logger.exception(
                "Could not enqueue retry for job %s; recovery is required",
                job_id,
            )
        return

    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job is not None and job.status == JobStatus.RUNNING:
            job.result = result_value
            job.error_message = None
            job.status = JobStatus.COMPLETED
            await session.commit()
            logger.info("Job %s completed", job_id)


def execute_job(job_id: str) -> None:
    """Synchronous entry point for RQ."""
    asyncio.run(_execute_job_async(job_id))
