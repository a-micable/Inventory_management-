"""Audit log endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntityType
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogResponse
from app.utils.response import success_response

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    entity_type: AuditEntityType | None = None,
    entity_id: UUID | None = None,
    action: AuditAction | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.core.permissions import require_permission
    require_permission(current_user.role, "audit:read")

    repo = AuditRepository(db)
    offset = (page - 1) * page_size
    logs = await repo.list_by_tenant(
        current_user.tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        limit=page_size,
        offset=offset,
    )
    return success_response({
        "items": [AuditLogResponse.model_validate(log).model_dump() for log in logs],
        "page": page,
        "page_size": page_size,
    })
