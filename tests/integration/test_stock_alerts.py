"""Integration tests for stock alert service."""

from __future__ import annotations

from app.domain.events import LowStockAlertEvent


class TestStockAlerts:
    def test_low_stock_event_fields(self):
        from uuid import uuid4
        event = LowStockAlertEvent(
            tenant_id=uuid4(),
            sku="SKU-001",
            current_quantity=3,
            reorder_point=10,
        )
        assert event.current_quantity < event.reorder_point
