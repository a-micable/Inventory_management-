"""Report job repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.report_job import ReportJob, ReportJobStatus
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[ReportJob]):
    model = ReportJob

    async def create_job(
        self,
        *,
        tenant_id: UUID,
        report_type: str,
        parameters: dict | None,
        requested_by_id: UUID | None,
    ) -> ReportJob:
        job = ReportJob(
            tenant_id=tenant_id,
            report_type=report_type,
            status=ReportJobStatus.PENDING,
            parameters=parameters,
            requested_by_id=requested_by_id,
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_by_id_for_tenant(self, tenant_id: UUID, job_id: UUID) -> ReportJob | None:
        stmt = select(ReportJob).where(
            ReportJob.tenant_id == tenant_id, ReportJob.id == job_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_job(
        self,
        job: ReportJob,
        *,
        status: str | None = None,
        result: dict | None = None,
        error_message: str | None = None,
        celery_task_id: str | None = None,
    ) -> ReportJob:
        if status:
            job.status = status
        if result is not None:
            job.result = result
        if error_message is not None:
            job.error_message = error_message
        if celery_task_id:
            job.celery_task_id = celery_task_id
        await self.session.flush()
        return job
