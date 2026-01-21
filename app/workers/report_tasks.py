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
