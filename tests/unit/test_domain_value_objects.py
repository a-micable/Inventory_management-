"""Unit tests for domain value objects."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.value_objects import Money, Quantity, SKU


class TestMoney:
    def test_add_same_currency(self):
        m1 = Money(Decimal("10.00"))
        m2 = Money(Decimal("5.50"))
        assert (m1 + m2).amount == Decimal("15.50")

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            Money(Decimal("-1"))


class TestSKU:
    def test_normalization(self):
        sku = SKU("  abc-123  ")
        assert sku.value == "ABC-123"


class TestQuantity:
    def test_subtract_insufficient(self):
        q = Quantity(5)
        with pytest.raises(ValueError):
            q.subtract(10)
