"""Warehouse schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase, TimestampSchema


class WarehouseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=2, max_length=32, pattern=r"^[A-Z0-9\-]+$")
    address: str | None = None
    city: str | None = None
    country: str | None = None


class WarehouseUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    is_active: bool | None = None


class WarehouseResponse(ORMBase, TimestampSchema):
    id: UUID
    name: str
    code: str
    address: str | None
    city: str | None
    country: str | None
    is_active: bool
    tenant_id: UUID
