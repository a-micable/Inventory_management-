"""Customer order model."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import OrderStatus
from app.database import Base
from app.models.base import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Order(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    warehouse_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    fulfilled_by_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    reservations: Mapped[list["StockReservation"]] = relationship("StockReservation")
