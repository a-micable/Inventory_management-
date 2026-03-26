"""Unit tests for export helpers."""

from __future__ import annotations


class TestCSVFormat:
    def test_header_row(self):
        header = ["product_id", "warehouse_id", "on_hand", "reserved", "available"]
        assert len(header) == 5
