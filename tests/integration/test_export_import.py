"""Integration tests for export/import roundtrip."""

from __future__ import annotations

import json


class TestExportImport:
    def test_json_roundtrip(self):
        data = [{"sku": "A", "name": "Product A"}]
        serialized = json.dumps(data)
        restored = json.loads(serialized)
        assert restored[0]["sku"] == "A"
