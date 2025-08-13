"""Stock transfer schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import TransferStatus
from app.schemas.common import ORMBase, TimestampSchema


class TransferLineCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., ge=1)


class TransferCreate(BaseModel):
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    lines: list[TransferLineCreate] = Field(..., min_length=1)
    notes: str | None = None


class TransferLineResponse(ORMBase, TimestampSchema):
    id: UUID
    product_id: UUID
    quantity: int


class TransferResponse(ORMBase, TimestampSchema):
    id: UUID
    transfer_number: str
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    status: TransferStatus
    notes: str | None
    lines: list[TransferLineResponse]
    tenant_id: UUID
