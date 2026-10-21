import asyncio
import logging
from sentinel.database import async_session_maker
from sentinel.models.job import Job, JobStatus

logger = logging.getLogger(__name__)


def execute_job(job_id: str) -> None:
    """Background worker task executed by RQ.

    Loads the job from PostgreSQL, updates status to RUNNING,
    processes the payload, and records COMPLETED or FAILED.
    """

    async def _run() -> None:
        async with async_session_maker() as session:
            job = await session.get(Job, job_id)
            if not job:
                logger.error(f"Job {job_id} not found in database.")
                return

            # Transition to RUNNING
            job.status = JobStatus.RUNNING
            await session.commit()

            try:
                logger.info("Executing job %s with payload: %s", job_id, job.payload)
                await asyncio.sleep(1)  # simulate work

                job.result = f"Successfully processed payload: {job.payload}"
                job.status = JobStatus.COMPLETED
            except Exception as e:
                logger.exception("Job %s failed with error: %s", job_id, str(e))
                job.error_message = str(e)
                job.status = JobStatus.FAILED

            await session.commit()

    asyncio.run(_run())
