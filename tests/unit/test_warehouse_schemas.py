"""Unit tests for warehouse schemas."""

from __future__ import annotations

from app.schemas.warehouse import WarehouseCreate


class TestWarehouseSchemas:
    def test_create_warehouse(self):
        w = WarehouseCreate(name="Main", code="WH-MAIN", city="Chicago")
        assert w.code == "WH-MAIN"
