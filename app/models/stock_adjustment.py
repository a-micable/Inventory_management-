"""Inventory stock adjustment audit trail."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import StockAdjustmentType
from app.database import Base
from app.models.base import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class StockAdjustment(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "stock_adjustments"

    inventory_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False
    )
    adjustment_type: Mapped[StockAdjustmentType] = mapped_column(
        Enum(StockAdjustmentType), nullable=False
    )
    quantity_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_before: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
