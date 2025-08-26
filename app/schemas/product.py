"""Product catalog schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase, TimestampSchema


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    unit_price: Decimal = Field(..., ge=0)
    reorder_point: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    unit_price: Decimal | None = Field(None, ge=0)
    reorder_point: int | None = Field(None, ge=0)
    is_active: bool | None = None


class ProductResponse(ORMBase, TimestampSchema):
    id: UUID
    sku: str
    name: str
    description: str | None
    category: str | None
    unit_price: Decimal
    reorder_point: int
    is_active: bool
    tenant_id: UUID
