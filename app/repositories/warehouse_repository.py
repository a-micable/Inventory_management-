"""Warehouse repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.warehouse import Warehouse
from app.repositories.base import BaseRepository


class WarehouseRepository(BaseRepository[Warehouse]):
    model = Warehouse

    async def get_by_code(self, tenant_id: UUID, code: str) -> Warehouse | None:
        stmt = select(Warehouse).where(
            Warehouse.tenant_id == tenant_id, Warehouse.code == code.upper()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: UUID, *, active_only: bool = True, limit: int = 50, offset: int = 0
    ) -> list[Warehouse]:
        stmt = select(Warehouse).where(Warehouse.tenant_id == tenant_id)
        if active_only:
            stmt = stmt.where(Warehouse.is_active.is_(True))
        stmt = stmt.order_by(Warehouse.name).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        stmt = select(Warehouse).where(Warehouse.tenant_id == tenant_id)
        return await self.count(stmt)

    async def create(
        self,
        *,
        tenant_id: UUID,
        name: str,
        code: str,
        address: str | None = None,
        city: str | None = None,
        country: str | None = None,
    ) -> Warehouse:
        warehouse = Warehouse(
            tenant_id=tenant_id,
            name=name,
            code=code.upper(),
            address=address,
            city=city,
            country=country,
            is_active=True,
        )
        self.session.add(warehouse)
        await self.session.flush()
        return warehouse
