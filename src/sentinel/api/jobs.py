from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from sentinel.database import get_db
from sentinel.models.job import Job, JobStatus
from sentinel.queue import job_queue
from sentinel.schemas.job import JobCreate, JobResponse
from sentinel.tasks.jobs import execute_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job_in: JobCreate, db: AsyncSession = Depends(get_db)) -> Job:
    job_id = str(uuid4())
    db_job = Job(
        id=job_id,
        name=job_in.name,
        payload=job_in.payload,
        status=JobStatus.QUEUED,  # Set initial status to QUEUED when dispatched
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    # Enqueue background task in RQ
    job_queue.enqueue(execute_job, job_id)

    return db_job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)) -> Job:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
