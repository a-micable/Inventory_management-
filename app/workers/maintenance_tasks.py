"""Scheduled maintenance tasks."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def purge_old_audit_logs():
    async def _execute():
        from sqlalchemy import delete
        from app.config import get_settings
        from app.database import session_scope
        from app.models.audit_log import AuditLog
        from app.utils.datetime_utils import utc_now

        settings = get_settings()
        cutoff = utc_now() - timedelta(days=settings.audit_retention_days)

        async with session_scope() as db:
            stmt = delete(AuditLog).where(AuditLog.created_at < cutoff)
            result = await db.execute(stmt)
            logger.info("Purged %d audit logs older than %s", result.rowcount, cutoff)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_execute())
    finally:
        loop.close()
