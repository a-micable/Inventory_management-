"""Product repository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_, select

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def get_by_sku(self, tenant_id: UUID, sku: str) -> Product | None:
        stmt = select(Product).where(Product.tenant_id == tenant_id, Product.sku == sku)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        search: str | None = None,
        category: str | None = None,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        stmt = select(Product).where(Product.tenant_id == tenant_id)
        if active_only:
            stmt = stmt.where(Product.is_active.is_(True))
        if category:
            stmt = stmt.where(Product.category == category)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
        stmt = stmt.order_by(Product.name).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID, *, search: str | None = None) -> int:
        stmt = select(Product).where(Product.tenant_id == tenant_id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
        return await self.count(stmt)

    async def create(
        self,
        *,
        tenant_id: UUID,
        sku: str,
        name: str,
        category: str | None = None,
        unit_price: Decimal = Decimal("0"),
        reorder_point: int = 0,
        description: str | None = None,
    ) -> Product:
        product = Product(
            tenant_id=tenant_id,
            sku=sku,
            name=name,
            category=category,
            unit_price=unit_price,
            reorder_point=reorder_point,
            description=description,
            is_active=True,
        )
        self.session.add(product)
        await self.session.flush()
        return product
