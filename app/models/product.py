"""Product catalog model."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Product(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"),)

    sku: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    reorder_point: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="products")
    inventory_items: Mapped[list["InventoryItem"]] = relationship("InventoryItem", back_populates="product")
