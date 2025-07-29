"""Background report generation job tracking."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ReportJobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportJob(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "report_jobs"

    report_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=ReportJobStatus.PENDING, nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_by_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
