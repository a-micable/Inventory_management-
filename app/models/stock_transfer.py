"""Inter-warehouse stock transfer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TransferStatus
from app.database import Base
from app.models.base import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin


class StockTransfer(Base, UUIDPrimaryKeyMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "stock_transfers"

    transfer_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source_warehouse_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    destination_warehouse_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    status: Mapped[TransferStatus] = mapped_column(
        Enum(TransferStatus), default=TransferStatus.PENDING, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    lines: Mapped[list["StockTransferLine"]] = relationship(
        "StockTransferLine", back_populates="transfer", cascade="all, delete-orphan"
    )


class StockTransferLine(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "stock_transfer_lines"

    transfer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("stock_transfers.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    transfer: Mapped["StockTransfer"] = relationship("StockTransfer", back_populates="lines")
