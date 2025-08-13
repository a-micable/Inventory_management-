"""Inventory and stock schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import ReservationStatus, StockAdjustmentType
from app.schemas.common import ORMBase, TimestampSchema


class InventoryItemResponse(ORMBase, TimestampSchema):
    id: UUID
    product_id: UUID
    warehouse_id: UUID
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    tenant_id: UUID


class StockAdjustmentCreate(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    adjustment_type: StockAdjustmentType
    quantity_delta: int = Field(..., description="Positive to add, negative to remove")
    reason: str | None = None
    reference: str | None = None


class StockAdjustmentResponse(ORMBase, TimestampSchema):
    id: UUID
    inventory_item_id: UUID
    adjustment_type: StockAdjustmentType
    quantity_delta: int
    quantity_before: int
    quantity_after: int
    reason: str | None
    reference: str | None


class StockReservationResponse(ORMBase, TimestampSchema):
    id: UUID
    order_id: UUID
    inventory_item_id: UUID
    quantity: int
    status: ReservationStatus
    expires_at: datetime | None
    reservation_ref: str
