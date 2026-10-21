from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from sentinel.models.job import JobStatus


class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    payload: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: JobStatus
    payload: str | None
    result: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
