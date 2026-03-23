"""Integration tests for report generation."""

from __future__ import annotations

from datetime import date

from app.schemas.report import SalesReportRequest


class TestReportRequests:
    def test_sales_date_range(self):
        req = SalesReportRequest(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 30),
        )
        assert (req.end_date - req.start_date).days == 29
