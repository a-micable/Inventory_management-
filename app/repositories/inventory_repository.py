"""Inventory repository with stock operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.enums import ReservationStatus, StockAdjustmentType
from app.models.inventory import InventoryItem
from app.models.stock_adjustment import StockAdjustment
from app.models.stock_reservation import StockReservation
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryItem]):
    model = InventoryItem

    async def get_or_create(
        self, tenant_id: UUID, product_id: UUID, warehouse_id: UUID
    ) -> InventoryItem:
        stmt = select(InventoryItem).where(
            InventoryItem.tenant_id == tenant_id,
            InventoryItem.product_id == product_id,
            InventoryItem.warehouse_id == warehouse_id,
        )
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        if item:
            return item
        item = InventoryItem(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity_on_hand=0,
            quantity_reserved=0,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def list_by_warehouse(
        self, tenant_id: UUID, warehouse_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> list[InventoryItem]:
        stmt = (
            select(InventoryItem)
            .options(selectinload(InventoryItem.product))
            .where(
                InventoryItem.tenant_id == tenant_id,
                InventoryItem.warehouse_id == warehouse_id,
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_tenant(
        self, tenant_id: UUID, *, warehouse_id: UUID | None = None, limit: int = 200, offset: int = 0
    ) -> list[InventoryItem]:
        stmt = select(InventoryItem).where(InventoryItem.tenant_id == tenant_id)
        if warehouse_id:
            stmt = stmt.where(InventoryItem.warehouse_id == warehouse_id)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def adjust_stock(
        self,
        *,
        item: InventoryItem,
        delta: int,
        adjustment_type: StockAdjustmentType,
        performed_by_id: UUID | None,
        reason: str | None = None,
        reference: str | None = None,
    ) -> StockAdjustment:
        before = item.quantity_on_hand
        after = before + delta
        if after < 0:
            raise ValueError("Stock cannot go negative")
        item.quantity_on_hand = after
        adjustment = StockAdjustment(
            tenant_id=item.tenant_id,
            inventory_item_id=item.id,
            adjustment_type=adjustment_type,
            quantity_delta=delta,
            quantity_before=before,
            quantity_after=after,
            reason=reason,
            reference=reference,
            performed_by_id=performed_by_id,
        )
        self.session.add(adjustment)
        await self.session.flush()
        return adjustment

    async def reserve_stock(
        self,
        *,
        item: InventoryItem,
        quantity: int,
        order_id: UUID,
        reservation_ref: str,
        expires_at,
    ) -> StockReservation:
        if item.quantity_available < quantity:
            raise ValueError("Insufficient available stock")
        item.quantity_reserved += quantity
        reservation = StockReservation(
            tenant_id=item.tenant_id,
            order_id=order_id,
            inventory_item_id=item.id,
            quantity=quantity,
            status=ReservationStatus.ACTIVE,
            reservation_ref=reservation_ref,
            expires_at=expires_at,
        )
        self.session.add(reservation)
        await self.session.flush()
        return reservation

    async def release_reservation(self, reservation: StockReservation) -> None:
        item = await self.get_by_id(reservation.inventory_item_id)
        if item:
            item.quantity_reserved = max(0, item.quantity_reserved - reservation.quantity)
        reservation.status = ReservationStatus.RELEASED
        await self.session.flush()

    async def consume_reservation(self, reservation: StockReservation) -> None:
        item = await self.get_by_id(reservation.inventory_item_id)
        if item:
            item.quantity_reserved = max(0, item.quantity_reserved - reservation.quantity)
            item.quantity_on_hand = max(0, item.quantity_on_hand - reservation.quantity)
        reservation.status = ReservationStatus.CONSUMED
        await self.session.flush()

    async def get_active_reservations(self, order_id: UUID) -> list[StockReservation]:
        stmt = select(StockReservation).where(
            StockReservation.order_id == order_id,
            StockReservation.status == ReservationStatus.ACTIVE,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
