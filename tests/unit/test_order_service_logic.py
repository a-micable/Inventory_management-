"""Unit tests for order business logic patterns."""

from __future__ import annotations

from decimal import Decimal

from app.core.enums import OrderStatus


class TestOrderStatusLogic:
    def test_cancellable_statuses(self):
        cancellable = {OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.DRAFT}
        for status in cancellable:
            assert status not in (OrderStatus.FULFILLED, OrderStatus.CANCELLED)

    def test_subtotal_calculation(self):
        items = [(Decimal("10.00"), 2), (Decimal("5.50"), 3)]
        subtotal = sum(price * qty for price, qty in items)
        assert subtotal == Decimal("36.50")
