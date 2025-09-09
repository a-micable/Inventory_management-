"""Audit log repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.core.enums import AuditAction, AuditEntityType
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    model = AuditLog

    async def create_log(
        self,
        *,
        tenant_id: UUID,
        entity_type: AuditEntityType,
        entity_id: UUID,
        action: AuditAction,
        description: str,
        actor_id: UUID | None = None,
        actor_email: str | None = None,
        changes: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        correlation_id: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            actor_id=actor_id,
            actor_email=actor_email,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        entity_type: AuditEntityType | None = None,
        entity_id: UUID | None = None,
        action: AuditAction | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditLog.entity_id == entity_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
