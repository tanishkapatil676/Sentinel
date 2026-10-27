import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

from sqlalchemy import update

from sentinel.database import async_session_maker
from sentinel.models.job import Job, JobStatus
from sentinel.queue import job_queue

logger = logging.getLogger(__name__)

CLAIMABLE_STATUSES = (
    JobStatus.PENDING,
    JobStatus.QUEUED,
)

TERMINAL_STATUSES = (
    JobStatus.COMPLETED,
    JobStatus.FAILED,
    JobStatus.CANCELLED,
)


class PermanentJobError(Exception):
    """Raised when a job fails in a way that should not be retried."""


async def process_job(name: str, payload: Any) -> Any:
    """
    Placeholder task processor.

    Replace this with actual task handlers when integrating the job types.
    """
    await asyncio.sleep(0.5)
    return f"Successfully processed job {name}. Payload: {payload}"


def _decode_payload(payload: Any) -> Any:
    if not isinstance(payload, str):
        return payload
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return payload


async def _execute_job_async(job_id: str) -> None:
    # Atomically claim only jobs that are eligible for execution.
    async with async_session_maker() as session:
        statement = (
            update(Job)
            .where(
                Job.id == job_id,
                Job.status.in_(CLAIMABLE_STATUSES),
            )
            .values(status=JobStatus.RUNNING)
            .returning(Job.id)
        )
        result = await session.execute(statement)
        claimed_id = result.scalar_one_or_none()
        await session.commit()

    # No returned ID means the job was missing or another worker
    # already claimed it, or it had an ineligible status.
    if claimed_id is None:
        logger.info("Job %s was not claimable; skipping.", job_id)
        return

    # Load the claimed job separately for processing.
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job is None:
            logger.error("Claimed job %s could not be loaded.", job_id)
            return

        name = job.name
        payload = _decode_payload(job.payload)

    try:
        output = await process_job(name, payload)

    except PermanentJobError as exc:
        async with async_session_maker() as session:
            job = await session.get(Job, job_id)
            if job is None:
                logger.error("Job %s disappeared after permanent failure.", job_id)
                return

            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            await session.commit()

        logger.error("Job %s failed permanently: %s", job_id, exc)
        return

    except Exception as exc:
        async with async_session_maker() as session:
            job = await session.get(Job, job_id)
            if job is None:
                logger.error("Job %s disappeared after transient failure.", job_id)
                return

            job.retry_count += 1
            job.error_message = str(exc)

            if job.retry_count <= job.max_retries:
                delay = min(2 ** job.retry_count, 60)
                job.status = JobStatus.PENDING
                await session.commit()

                logger.warning(
                    "Job %s retry %s/%s scheduled in %s seconds.",
                    job_id, job.retry_count, job.max_retries, delay,
                )

                # Queue interaction occurs after the database commit.
                job_queue.enqueue_in(
                    timedelta(seconds=delay),
                    execute_job,
                    job_id,
                )
            else:
                job.status = JobStatus.FAILED
                await session.commit()
                logger.error(
                    "Job %s exhausted its retry limit (%s).",
                    job_id, job.max_retries,
                )
        return

    # Persist successful result.
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job is None:
            logger.error("Job %s disappeared before completion was saved.", job_id)
            return

        job.status = JobStatus.COMPLETED
        job.result = (
            output if isinstance(output, str)
            else json.dumps(output, default=str)
        )
        job.error_message = None
        await session.commit()

    logger.info("Job %s completed successfully.", job_id)


def execute_job(job_id: str) -> None:
    """Synchronous entry point for an RQ worker."""
    asyncio.run(_execute_job_async(job_id))
