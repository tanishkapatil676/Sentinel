import hashlib
import json
import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from sentinel.database import async_session_maker
from sentinel.jobs.handlers import compute_numeric_summary
from sentinel.models import IdempotencyRecord, Job, JobStatus
from sentinel.queue import job_queue
from sentinel.tasks.jobs import execute_job

logger = logging.getLogger(__name__)
router = APIRouter(tags=["jobs"])


class JobCreateRequest(BaseModel):
    name: str = Field(default="numeric_summary", min_length=1, max_length=255)
    payload: dict[str, Any]


def serialize_job(job: Job) -> dict[str, Any]:
    result = None
    if job.result is not None:
        try:
            result = json.loads(job.result)
        except (json.JSONDecodeError, TypeError):
            result = job.result

    return {
        "id": job.id,
        "name": job.name,
        "status": job.status.value,
        "payload": json.loads(job.payload) if job.payload else None,
        "result": result,
        "error_message": job.error_message,
        "retry_count": job.retry_count,
        "max_retries": job.max_retries,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }


@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    request: JobCreateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if request.name == "numeric_summary":
        try:
            compute_numeric_summary(request.payload)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid numeric_summary payload: {exc}",
            ) from exc

    canonical_request = json.dumps(
        {"name": request.name, "payload": request.payload},
        sort_keys=True,
        separators=(",", ":"),
    )
    fingerprint = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()

    if idempotency_key is not None:
        if not idempotency_key.strip() or len(idempotency_key) > 255:
            raise HTTPException(
                status_code=400,
                detail="Idempotency-Key must contain 1–255 characters.",
            )

    job_id = str(uuid.uuid4())

    async with async_session_maker() as session:
        if idempotency_key:
            existing_record = await session.get(
                IdempotencyRecord, idempotency_key
            )
            if existing_record:
                if existing_record.request_fingerprint != fingerprint:
                    raise HTTPException(
                        status_code=409,
                        detail="Idempotency-Key was already used with a different request.",
                    )
                existing_job = await session.get(Job, existing_record.job_id)
                if existing_job is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Idempotency record references a missing job.",
                    )
                return serialize_job(existing_job)

        job = Job(
            id=job_id,
            name=request.name,
            status=JobStatus.QUEUED,
            payload=json.dumps(request.payload),
        )
        session.add(job)

        if idempotency_key:
            session.add(
                IdempotencyRecord(
                    idempotency_key=idempotency_key,
                    job_id=job_id,
                    request_fingerprint=fingerprint,
                )
            )

        try:
            await session.commit()
            await session.refresh(job)
        except IntegrityError as exc:
            await session.rollback()
            logger.warning("Job creation conflict: %s", exc)
            raise HTTPException(
                status_code=409,
                detail="Job creation conflicted with an existing record. Retry with a fresh request.",
            ) from exc

        response = serialize_job(job)

    # Persist the job before dispatching it to Redis.
    try:
        job_queue.enqueue(execute_job, job_id)
    except Exception as exc:
        logger.exception("Queue dispatch failed for job %s", job_id)
        async with async_session_maker() as session:
            stored_job = await session.get(Job, job_id)
            if stored_job is not None and stored_job.status == JobStatus.QUEUED:
                stored_job.status = JobStatus.FAILED
                stored_job.error_message = "Queue dispatch failed; check Redis and worker availability."
                await session.commit()
        raise HTTPException(
            status_code=503,
            detail="Job was persisted but could not be queued. Check Redis availability.",
        ) from exc

    return response


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        return serialize_job(job)
