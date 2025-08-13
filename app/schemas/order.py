"""Order processing schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import OrderStatus
from app.schemas.common import ORMBase, TimestampSchema


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., ge=1)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: EmailStr | None = None
    warehouse_id: UUID
    items: list[OrderItemCreate] = Field(..., min_length=1)
    notes: str | None = None


class OrderItemResponse(ORMBase, TimestampSchema):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderResponse(ORMBase, TimestampSchema):
    id: UUID
    order_number: str
    status: OrderStatus
    customer_name: str
    customer_email: str | None
    warehouse_id: UUID
    subtotal: Decimal
    notes: str | None
    items: list[OrderItemResponse]
    tenant_id: UUID


class OrderCancelRequest(BaseModel):
    reason: str | None = None
