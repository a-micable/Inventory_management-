"""Order repository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.enums import OrderStatus
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order

    async def get_with_items(self, order_id: UUID) -> Order | None:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        status: OrderStatus | None = None,
        warehouse_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.tenant_id == tenant_id)
        )
        if status:
            stmt = stmt.where(Order.status == status)
        if warehouse_id:
            stmt = stmt.where(Order.warehouse_id == warehouse_id)
        stmt = stmt.order_by(Order.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID, *, status: OrderStatus | None = None) -> int:
        stmt = select(Order).where(Order.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Order.status == status)
        return await self.count(stmt)

    async def create_order(
        self,
        *,
        tenant_id: UUID,
        order_number: str,
        customer_name: str,
        warehouse_id: UUID,
        created_by_id: UUID | None,
        customer_email: str | None = None,
        notes: str | None = None,
        items: list[tuple[UUID, int, Decimal]],
    ) -> Order:
        subtotal = sum(price * qty for _, qty, price in items)
        order = Order(
            tenant_id=tenant_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            customer_name=customer_name,
            customer_email=customer_email,
            warehouse_id=warehouse_id,
            subtotal=subtotal,
            notes=notes,
            created_by_id=created_by_id,
        )
        self.session.add(order)
        await self.session.flush()

        for product_id, qty, price in items:
            line = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=qty,
                unit_price=price,
                line_total=price * qty,
            )
            self.session.add(line)
        await self.session.flush()
        await self.session.refresh(order, ["items"])
        return order

    async def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        await self.session.flush()
        return order
