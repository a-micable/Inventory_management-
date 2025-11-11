"""Report generation endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.report import InventoryReportRequest, SalesReportRequest
from app.services.report_service import ReportService
from app.utils.response import success_response

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/inventory")
async def inventory_report(
    data: InventoryReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReportService(db)
    report = await service.inventory_report(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(report.model_dump())


@router.post("/sales")
async def sales_report(
    data: SalesReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReportService(db)
    report = await service.sales_report(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(report.model_dump())


@router.post("/async/{report_type}")
async def async_report(
    report_type: str,
    parameters: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReportService(db)
    job = await service.enqueue_report(
        current_user.tenant_id,
        report_type,
        parameters,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )
    return success_response(job.model_dump())
