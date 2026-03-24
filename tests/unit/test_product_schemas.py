"""Unit tests for product schemas."""

from __future__ import annotations

from decimal import Decimal

from app.schemas.product import ProductCreate, ProductUpdate


class TestProductSchemas:
    def test_create_product(self):
        p = ProductCreate(sku="SKU-001", name="Widget", unit_price=Decimal("9.99"))
        assert p.reorder_point == 0

    def test_partial_update(self):
        u = ProductUpdate(name="New Name")
        assert u.unit_price is None
