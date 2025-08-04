"""Per-warehouse inventory stock levels."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class InventoryItem(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "inventory_items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "product_id", "warehouse_id", name="uq_inventory_product_wh"),
    )

    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    warehouse_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_reserved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="inventory_items")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="inventory_items")

    @property
    def quantity_available(self) -> int:
        return max(0, self.quantity_on_hand - self.quantity_reserved)
