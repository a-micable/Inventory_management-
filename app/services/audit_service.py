"""Audit logging service."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntityType
from app.repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AuditRepository(session)

    async def log(
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
    ) -> None:
        await self.repo.create_log(
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
        logger.info(
            "Audit: %s %s on %s/%s",
            action.value,
            description,
            entity_type.value,
            entity_id,
            extra={"tenant_id": str(tenant_id), "actor_id": str(actor_id) if actor_id else None},
        )
