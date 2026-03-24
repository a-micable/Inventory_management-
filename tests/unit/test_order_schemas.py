"""Unit tests for order schemas."""

from __future__ import annotations

from uuid import uuid4

from app.schemas.order import OrderCreate, OrderItemCreate


class TestOrderSchemas:
    def test_order_create(self):
        order = OrderCreate(
            customer_name="John Doe",
            warehouse_id=uuid4(),
            items=[OrderItemCreate(product_id=uuid4(), quantity=2)],
        )
        assert len(order.items) == 1
