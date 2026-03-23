"""Integration tests for order lifecycle."""

from __future__ import annotations

import pytest

from app.core.enums import OrderStatus

pytestmark = pytest.mark.asyncio


class TestOrderLifecycle:
    def test_order_status_enum_values(self):
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.FULFILLED.value == "fulfilled"
        assert OrderStatus.CANCELLED.value == "cancelled"
