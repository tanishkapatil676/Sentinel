from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from sentinel.database import Base


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_keys"

    idempotency_key = Column(String, primary_key=True, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    request_fingerprint = Column(String(64), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    job = relationship("Job", backref="idempotency_record")
