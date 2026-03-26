"""Unit tests for domain policies."""

from __future__ import annotations

import pytest

from app.core.enums import OrderStatus, TransferStatus
from app.domain.policies import OrderPolicy, StockPolicy, TransferPolicy


class TestOrderPolicy:
    def test_can_fulfill_confirmed(self):
        OrderPolicy.can_fulfill(OrderStatus.CONFIRMED)

    def test_cannot_fulfill_cancelled(self):
        with pytest.raises(Exception):
            OrderPolicy.can_fulfill(OrderStatus.CANCELLED)


class TestStockPolicy:
    def test_validate_adjustment(self):
        result = StockPolicy.validate_adjustment(100, -30)
        assert result == 70

    def test_negative_stock_rejected(self):
        with pytest.raises(Exception):
            StockPolicy.validate_adjustment(10, -20)


class TestTransferPolicy:
    def test_same_warehouse_rejected(self):
        from uuid import uuid4
        wid = uuid4()
        with pytest.raises(Exception):
            TransferPolicy.validate_warehouses(wid, wid)
