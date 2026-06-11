"""Generate Celery worker modules."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "app/workers/__init__.py": '"""Background worker tasks."""\n',
        "app/workers/celery_app.py": _CELERY,
        "app/workers/report_tasks.py": _REPORT,
        "app/workers/inventory_tasks.py": _INVENTORY,
        "app/workers/maintenance_tasks.py": _MAINTENANCE,
    }


_CELERY = '''
"""Celery application configuration."""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "inventory_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.report_tasks",
        "app.workers.inventory_tasks",
        "app.workers.maintenance_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "expire-stale-reservations": {
            "task": "app.workers.inventory_tasks.expire_stale_reservations",
            "schedule": 3600.0,
        },
        "warm-inventory-cache": {
            "task": "app.workers.inventory_tasks.warm_inventory_cache",
            "schedule": 1800.0,
        },
        "purge-old-audit-logs": {
            "task": "app.workers.maintenance_tasks.purge_old_audit_logs",
            "schedule": 86400.0,
        },
    },
)
'''

_REPORT = '''
"""Async report generation tasks."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_report_async(self, job_id: str, tenant_id: str, report_type: str, parameters: dict):
    async def _execute():
        from app.database import session_scope
        from app.models.report_job import ReportJobStatus
        from app.repositories.report_repository import ReportRepository
        from app.schemas.report import InventoryReportRequest, SalesReportRequest
        from app.services.report_service import ReportService

        async with session_scope() as db:
            repo = ReportRepository(db)
            job = await repo.get_by_id_for_tenant(UUID(tenant_id), UUID(job_id))
            if not job:
                logger.error("Report job %s not found", job_id)
                return

            await repo.update_job(job, status=ReportJobStatus.RUNNING)
            service = ReportService(db)

            try:
                if report_type == "inventory":
                    params = InventoryReportRequest.model_validate(parameters)
                    result = await service.inventory_report(
                        UUID(tenant_id),
                        params,
                        actor_id=job.requested_by_id,
                        actor_email=None,
                        actor_role=None,  # type: ignore[arg-type]
                    )
                elif report_type == "sales":
                    params = SalesReportRequest.model_validate(parameters)
                    result = await service.sales_report(
                        UUID(tenant_id),
                        params,
                        actor_id=job.requested_by_id,
                        actor_email=None,
                        actor_role=None,  # type: ignore[arg-type]
                    )
                else:
                    raise ValueError(f"Unknown report type: {report_type}")

                await repo.update_job(
                    job, status=ReportJobStatus.COMPLETED, result=result.model_dump()
                )
            except Exception as exc:
                logger.exception("Report job %s failed", job_id)
                await repo.update_job(
                    job, status=ReportJobStatus.FAILED, error_message=str(exc)
                )
                raise self.retry(exc=exc) from exc

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_execute())
    finally:
        loop.close()
'''

_INVENTORY = '''
"""Inventory background tasks."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def expire_stale_reservations():
    async def _execute():
        from sqlalchemy import select, update
        from app.core.enums import ReservationStatus
        from app.database import session_scope
        from app.models.stock_reservation import StockReservation
        from app.repositories.inventory_repository import InventoryRepository
        from app.utils.datetime_utils import utc_now

        async with session_scope() as db:
            now = utc_now()
            stmt = select(StockReservation).where(
                StockReservation.status == ReservationStatus.ACTIVE,
                StockReservation.expires_at < now,
            )
            result = await db.execute(stmt)
            reservations = list(result.scalars().all())
            repo = InventoryRepository(db)
            for reservation in reservations:
                await repo.release_reservation(reservation)
                reservation.status = ReservationStatus.EXPIRED
            logger.info("Expired %d stale reservations", len(reservations))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_execute())
    finally:
        loop.close()


@celery_app.task
def warm_inventory_cache():
    async def _execute():
        from sqlalchemy import select
        from app.core.cache import cache_set
        from app.core.constants import INVENTORY_CACHE_PREFIX
        from app.database import session_scope
        from app.models.tenant import Tenant

        async with session_scope() as db:
            result = await db.execute(select(Tenant).where(Tenant.is_active.is_(True)))
            tenants = list(result.scalars().all())
            for tenant in tenants:
                await cache_set(
                    f"{INVENTORY_CACHE_PREFIX}{tenant.id}:warm",
                    {"warmed_at": str(utc_now())},
                    ttl=1800,
                )
            logger.info("Warmed inventory cache for %d tenants", len(tenants))

    from app.utils.datetime_utils import utc_now
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_execute())
    finally:
        loop.close()
'''

_MAINTENANCE = '''
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
'''
