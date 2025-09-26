"""Inventory management service."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import INVENTORY_CACHE_PREFIX, RESERVATION_TTL_HOURS
from app.core.enums import AuditAction, AuditEntityType, UserRole
from app.core.exceptions import InsufficientStockError, NotFoundError, ValidationError
from app.core.permissions import require_permission
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.inventory import (
    InventoryItemResponse,
    StockAdjustmentCreate,
    StockAdjustmentResponse,
)
from app.services.audit_service import AuditService
from app.services.number_generator import generate_reservation_ref
from app.utils.datetime_utils import utc_now
from app.utils.pagination import Page, PageParams


class InventoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = InventoryRepository(session)
        self.product_repo = ProductRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.audit = AuditService(session)

    async def list_inventory(
        self,
        tenant_id: UUID,
        params: PageParams,
        *,
        warehouse_id: UUID | None = None,
        actor_role: UserRole,
    ) -> Page[InventoryItemResponse]:
        require_permission(actor_role, "inventory:read")
        items = await self.repo.list_by_tenant(
            tenant_id, warehouse_id=warehouse_id, limit=params.page_size, offset=params.offset
        )
        responses = [
            InventoryItemResponse(
                id=i.id,
                product_id=i.product_id,
                warehouse_id=i.warehouse_id,
                quantity_on_hand=i.quantity_on_hand,
                quantity_reserved=i.quantity_reserved,
                quantity_available=i.quantity_available,
                tenant_id=i.tenant_id,
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in items
        ]
        return Page(items=responses, total=len(responses), page=params.page, page_size=params.page_size)

    async def adjust_stock(
        self,
        tenant_id: UUID,
        data: StockAdjustmentCreate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> StockAdjustmentResponse:
        require_permission(actor_role, "inventory:adjust")
        product = await self.product_repo.get_by_id(data.product_id)
        warehouse = await self.warehouse_repo.get_by_id(data.warehouse_id)
        if not product or product.tenant_id != tenant_id:
            raise NotFoundError("Product not found")
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise NotFoundError("Warehouse not found")
        if data.quantity_delta == 0:
            raise ValidationError("Adjustment delta cannot be zero")

        item = await self.repo.get_or_create(tenant_id, data.product_id, data.warehouse_id)
        try:
            adjustment = await self.repo.adjust_stock(
                item=item,
                delta=data.quantity_delta,
                adjustment_type=data.adjustment_type,
                performed_by_id=actor_id,
                reason=data.reason,
                reference=data.reference,
            )
        except ValueError as exc:
            raise InsufficientStockError(str(exc)) from exc

        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.INVENTORY,
            entity_id=item.id,
            action=AuditAction.ADJUST,
            description=(
                f"Stock adjustment {data.adjustment_type.value}: "
                f"{data.quantity_delta:+d} for product {product.sku} at {warehouse.code}"
            ),
            actor_id=actor_id,
            actor_email=actor_email,
            changes={
                "quantity_before": adjustment.quantity_before,
                "quantity_after": adjustment.quantity_after,
                "delta": data.quantity_delta,
            },
        )
        return StockAdjustmentResponse.model_validate(adjustment)

    async def reserve_for_order(
        self,
        tenant_id: UUID,
        order_id: UUID,
        product_id: UUID,
        warehouse_id: UUID,
        quantity: int,
        *,
        actor_id: UUID | None = None,
        actor_email: str | None = None,
    ) -> None:
        item = await self.repo.get_or_create(tenant_id, product_id, warehouse_id)
        expires_at = utc_now() + timedelta(hours=RESERVATION_TTL_HOURS)
        try:
            reservation = await self.repo.reserve_stock(
                item=item,
                quantity=quantity,
                order_id=order_id,
                reservation_ref=generate_reservation_ref(),
                expires_at=expires_at,
            )
        except ValueError as exc:
            raise InsufficientStockError(str(exc)) from exc

        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.RESERVATION,
            entity_id=reservation.id,
            action=AuditAction.RESERVE,
            description=f"Reserved {quantity} units for order {order_id}",
            actor_id=actor_id,
            actor_email=actor_email,
        )

    async def release_order_reservations(
        self,
        tenant_id: UUID,
        order_id: UUID,
        *,
        actor_id: UUID | None = None,
        actor_email: str | None = None,
    ) -> None:
        reservations = await self.repo.get_active_reservations(order_id)
        for reservation in reservations:
            await self.repo.release_reservation(reservation)
            await self.audit.log(
                tenant_id=tenant_id,
                entity_type=AuditEntityType.RESERVATION,
                entity_id=reservation.id,
                action=AuditAction.RELEASE,
                description=f"Released reservation for order {order_id}",
                actor_id=actor_id,
                actor_email=actor_email,
            )
