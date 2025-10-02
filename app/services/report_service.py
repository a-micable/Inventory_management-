"""Report generation service with caching and async jobs."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import cache_get, cache_set
from app.core.constants import REPORT_CACHE_PREFIX
from app.core.enums import AuditAction, AuditEntityType, OrderStatus, UserRole
from app.core.permissions import require_permission
from app.models.inventory import InventoryItem
from app.models.order import Order
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    InventoryReportRequest,
    InventoryReportResponse,
    InventoryReportRow,
    ReportJobResponse,
    SalesReportRequest,
    SalesReportResponse,
    SalesReportRow,
)
from app.services.audit_service import AuditService
from app.utils.datetime_utils import utc_now


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ReportRepository(session)
        self.audit = AuditService(session)

    async def inventory_report(
        self,
        tenant_id: UUID,
        params: InventoryReportRequest,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> InventoryReportResponse:
        require_permission(actor_role, "reports:read")
        cache_key = f"{REPORT_CACHE_PREFIX}inventory:{tenant_id}:{params.model_dump_json()}"
        cached = await cache_get(cache_key)
        if cached:
            return InventoryReportResponse.model_validate(cached)

        stmt = (
            select(InventoryItem)
            .join(Product)
            .join(Warehouse)
            .where(InventoryItem.tenant_id == tenant_id)
            .options(selectinload(InventoryItem.product), selectinload(InventoryItem.warehouse))
        )
        if params.warehouse_id:
            stmt = stmt.where(InventoryItem.warehouse_id == params.warehouse_id)
        if params.category:
            stmt = stmt.where(Product.category == params.category)
        if not params.include_zero_stock:
            stmt = stmt.where(InventoryItem.quantity_on_hand > 0)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        rows: list[InventoryReportRow] = []
        total_value = Decimal("0")
        for item in items:
            stock_value = item.product.unit_price * item.quantity_on_hand
            total_value += stock_value
            rows.append(
                InventoryReportRow(
                    product_id=item.product_id,
                    sku=item.product.sku,
                    product_name=item.product.name,
                    warehouse_id=item.warehouse_id,
                    warehouse_code=item.warehouse.code,
                    quantity_on_hand=item.quantity_on_hand,
                    quantity_reserved=item.quantity_reserved,
                    quantity_available=item.quantity_available,
                    reorder_point=item.product.reorder_point,
                    below_reorder=item.quantity_on_hand <= item.product.reorder_point,
                    unit_price=item.product.unit_price,
                    stock_value=stock_value,
                )
            )

        report = InventoryReportResponse(
            generated_at=utc_now(),
            total_skus=len(rows),
            total_stock_value=total_value,
            rows=rows,
        )
        await cache_set(cache_key, report.model_dump())
        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.REPORT,
            entity_id=tenant_id,
            action=AuditAction.CREATE,
            description="Generated inventory report",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        return report

    async def sales_report(
        self,
        tenant_id: UUID,
        params: SalesReportRequest,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> SalesReportResponse:
        require_permission(actor_role, "reports:read")
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(
                Order.tenant_id == tenant_id,
                Order.status == OrderStatus.FULFILLED,
                Order.created_at >= datetime.combine(params.start_date, datetime.min.time()).replace(tzinfo=timezone.utc),
                Order.created_at <= datetime.combine(params.end_date, datetime.max.time()).replace(tzinfo=timezone.utc),
            )
        )
        if params.warehouse_id:
            stmt = stmt.where(Order.warehouse_id == params.warehouse_id)

        result = await self.session.execute(stmt)
        orders = list(result.scalars().all())

        rows = [
            SalesReportRow(
                order_id=o.id,
                order_number=o.order_number,
                fulfilled_at=o.updated_at,
                customer_name=o.customer_name,
                warehouse_id=o.warehouse_id,
                line_count=len(o.items),
                subtotal=o.subtotal,
            )
            for o in orders
        ]
        total_revenue = sum((r.subtotal for r in rows), Decimal("0"))

        report = SalesReportResponse(
            generated_at=utc_now(),
            period_start=params.start_date,
            period_end=params.end_date,
            total_orders=len(rows),
            total_revenue=total_revenue,
            rows=rows,
        )
        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.REPORT,
            entity_id=tenant_id,
            action=AuditAction.CREATE,
            description=f"Generated sales report {params.start_date} to {params.end_date}",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        return report

    async def enqueue_report(
        self,
        tenant_id: UUID,
        report_type: str,
        parameters: dict,
        *,
        actor_id: UUID,
        actor_role: UserRole,
    ) -> ReportJobResponse:
        require_permission(actor_role, "reports:read")
        job = await self.repo.create_job(
            tenant_id=tenant_id,
            report_type=report_type,
            parameters=parameters,
            requested_by_id=actor_id,
        )
        from app.workers.report_tasks import generate_report_async
        task = generate_report_async.delay(str(job.id), str(tenant_id), report_type, parameters)
        await self.repo.update_job(job, celery_task_id=task.id)
        return ReportJobResponse(
            id=job.id,
            report_type=job.report_type,
            status=job.status,
            created_at=job.created_at,
        )
