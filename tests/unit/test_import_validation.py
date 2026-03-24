"""Unit tests for import validation."""

from __future__ import annotations

import csv
import io


class TestCSVParsing:
    def test_dict_reader(self):
        content = "sku,name,unit_price\nSKU-001,Widget,9.99\n"
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["sku"] == "SKU-001"
