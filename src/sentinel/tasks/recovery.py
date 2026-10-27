import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from sentinel.database import AsyncSessionLocal
from sentinel.models.job import Job, JobStatus

logger = logging.getLogger(__name__)


async def recover_stale_jobs(
    stale_threshold_minutes: int = 15,
    db_session=None,
) -> int:
    """
    Recover jobs stuck in RUNNING beyond the configured threshold.

    Jobs with retries remaining are reset to PENDING.
    Jobs that exceed their retry limit are marked FAILED.

    Returns the number of stale jobs processed.
    """
    if stale_threshold_minutes < 0:
        raise ValueError("stale_threshold_minutes must be non-negative")

    threshold_time = (
        datetime.now(timezone.utc)
        - timedelta(minutes=stale_threshold_minutes)
    )

    if db_session is not None:
        count = await _process_stale_jobs(db_session, threshold_time)
        await db_session.commit()
        return count

    async with AsyncSessionLocal() as session:
        async with session.begin():
            count = await _process_stale_jobs(session, threshold_time)
        return count


async def _process_stale_jobs(session, threshold_time) -> int:
    result = await session.execute(
        select(Job)
        .where(
            Job.status == JobStatus.RUNNING,
            Job.updated_at < threshold_time,
        )
        .with_for_update()
    )
    stale_jobs = result.scalars().all()

    for job in stale_jobs:
        logger.warning(
            "event=stale_job_detected job_id=%s last_updated=%s "
            "retry_count=%s max_retries=%s",
            job.id,
            job.updated_at,
            job.retry_count,
            job.max_retries,
        )

        job.retry_count += 1
        job.error_message = (
            "Recovered from stale RUNNING state (exceeded threshold)."
        )

        if job.retry_count <= job.max_retries:
            job.status = JobStatus.PENDING
            logger.info(
                "event=stale_job_recovered_to_pending job_id=%s new_attempt=%s",
                job.id,
                job.retry_count,
            )
        else:
            job.status = JobStatus.FAILED
            logger.error(
                "event=stale_job_exhausted_retries job_id=%s "
                "final_status=FAILED",
                job.id,
            )

    return len(stale_jobs)
