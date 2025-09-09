"""Stock transfer repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.enums import TransferStatus
from app.models.stock_transfer import StockTransfer, StockTransferLine
from app.repositories.base import BaseRepository


class TransferRepository(BaseRepository[StockTransfer]):
    model = StockTransfer

    async def get_with_lines(self, transfer_id: UUID) -> StockTransfer | None:
        stmt = (
            select(StockTransfer)
            .options(selectinload(StockTransfer.lines))
            .where(StockTransfer.id == transfer_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: UUID, *, limit: int = 50, offset: int = 0
    ) -> list[StockTransfer]:
        stmt = (
            select(StockTransfer)
            .options(selectinload(StockTransfer.lines))
            .where(StockTransfer.tenant_id == tenant_id)
            .order_by(StockTransfer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_transfer(
        self,
        *,
        tenant_id: UUID,
        transfer_number: str,
        source_warehouse_id: UUID,
        destination_warehouse_id: UUID,
        created_by_id: UUID | None,
        lines: list[tuple[UUID, int]],
        notes: str | None = None,
    ) -> StockTransfer:
        transfer = StockTransfer(
            tenant_id=tenant_id,
            transfer_number=transfer_number,
            source_warehouse_id=source_warehouse_id,
            destination_warehouse_id=destination_warehouse_id,
            status=TransferStatus.PENDING,
            notes=notes,
            created_by_id=created_by_id,
        )
        self.session.add(transfer)
        await self.session.flush()
        for product_id, qty in lines:
            line = StockTransferLine(transfer_id=transfer.id, product_id=product_id, quantity=qty)
            self.session.add(line)
        await self.session.flush()
        await self.session.refresh(transfer, ["lines"])
        return transfer
