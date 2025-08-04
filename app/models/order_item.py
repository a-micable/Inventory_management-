"""Line items within an order."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class OrderItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "order_items"

    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
