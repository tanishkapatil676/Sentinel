
import hashlib
import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel.database import get_db
from sentinel.models.idempotency import IdempotencyRecord
from sentinel.models.job import Job, JobStatus
from sentinel.queue import job_queue
from sentinel.tasks.jobs import execute_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)
    max_retries: int = Field(default=3, ge=0, le=10)


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: JobStatus
    payload: dict[str, Any] | None
    result: Any = None
    error_message: str | None
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime


def _decode_json(value: str | None) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value


def _response_for(job: Job) -> dict[str, Any]:
    return {
        "id": job.id,
        "name": job.name,
        "status": job.status.value,
        "payload": _decode_json(job.payload),
        "result": _decode_json(job.result),
        "error_message": job.error_message,
        "retry_count": job.retry_count,
        "max_retries": job.max_retries,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


def _fingerprint(request: JobCreateRequest) -> str:
    canonical = json.dumps(
        request.model_dump(),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def _enqueue_or_mark_failed(
    session: AsyncSession,
    job: Job,
) -> None:
    try:
        job_queue.enqueue(execute_job, job.id)
    except Exception as exc:
        logger.exception("Queue submission failed for job %s", job.id)
        job.status = JobStatus.FAILED
        job.error_message = f"Queue submission failed: {type(exc).__name__}"
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "Job was saved but could not be submitted to the queue.",
                "job_id": job.id,
                "status": job.status.value,
            },
        ) from exc


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateRequest,
    session: AsyncSession = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    fingerprint = _fingerprint(request)

    if idempotency_key is not None:
        idempotency_key = idempotency_key.strip()
        if not idempotency_key or len(idempotency_key) > 255:
            raise HTTPException(
                status_code=400,
                detail="Idempotency-Key must contain 1–255 characters.",
            )

        existing_result = await session.execute(
            select(IdempotencyRecord).where(
                IdempotencyRecord.idempotency_key == idempotency_key
            )
        )
        existing_record = existing_result.scalar_one_or_none()

        if existing_record is not None:
            if existing_record.request_fingerprint != fingerprint:
                raise HTTPException(
                    status_code=409,
                    detail="This Idempotency-Key was already used for a different request.",
                )

            existing_job = await session.get(Job, existing_record.job_id)
            if existing_job is None:
                raise HTTPException(
                    status_code=500,
                    detail="Idempotency record references a missing job.",
                )

            return JSONResponse(
                status_code=200,
                content=json.loads(
                    json.dumps(_response_for(existing_job), default=str)
                ),
            )

    job = Job(
        id=str(uuid4()),
        name=request.name,
        status=JobStatus.QUEUED,
        payload=json.dumps(
            request.payload,
            sort_keys=True,
            allow_nan=False,
        ),
        max_retries=request.max_retries,
    )
    session.add(job)

    if idempotency_key is not None:
        session.add(
            IdempotencyRecord(
                idempotency_key=idempotency_key,
                job_id=job.id,
                request_fingerprint=fingerprint,
            )
        )

    try:
        await session.commit()
        await session.refresh(job)
    except Exception:
        await session.rollback()
        raise

    await _enqueue_or_mark_failed(session, job)
    await session.refresh(job)
    return _response_for(job)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Job)
        .order_by(Job.created_at.desc(), Job.id)
        .limit(limit)
        .offset(offset)
    )
    return [_response_for(job) for job in result.scalars().all()]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_db),
):
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _response_for(job)


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: str,
    session: AsyncSession = Depends(get_db),
):
    job = await session.get(Job, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.status != JobStatus.FAILED:
        raise HTTPException(
            status_code=409,
            detail=f"Only FAILED jobs can be manually retried; current status is {job.status.value}.",
        )

    job.status = JobStatus.QUEUED
    job.error_message = None

    await session.commit()
    await session.refresh(job)

    await _enqueue_or_mark_failed(session, job)
    await session.refresh(job)
    return _response_for(job)
