"""Audit log schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import AuditAction, AuditEntityType
from app.schemas.common import ORMBase


class AuditLogResponse(ORMBase):
    id: UUID
    entity_type: AuditEntityType
    entity_id: UUID
    action: AuditAction
    actor_id: UUID | None
    actor_email: str | None
    description: str
    changes: dict | None
    ip_address: str | None
    correlation_id: str | None
    created_at: datetime
    tenant_id: UUID


class AuditLogFilter(BaseModel):
    entity_type: AuditEntityType | None = None
    entity_id: UUID | None = None
    action: AuditAction | None = None
    actor_id: UUID | None = None
