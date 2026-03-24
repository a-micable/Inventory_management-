"""Unit tests for report schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.schemas.report import InventoryReportRequest, SalesReportRequest


class TestReportSchemas:
    def test_inventory_report_request_defaults(self):
        req = InventoryReportRequest()
        assert req.include_zero_stock is False
        assert req.warehouse_id is None

    def test_sales_report_request(self):
        req = SalesReportRequest(start_date=date(2025, 1, 1), end_date=date(2025, 12, 31))
        assert req.start_date < req.end_date
