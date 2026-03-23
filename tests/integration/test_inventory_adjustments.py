"""Integration tests for inventory adjustments."""

from __future__ import annotations

from app.core.enums import StockAdjustmentType


class TestAdjustmentTypes:
    def test_all_types_defined(self):
        types = list(StockAdjustmentType)
        assert len(types) >= 5
        assert StockAdjustmentType.RECEIPT in types
