"""Unit tests for product search index."""

from __future__ import annotations

from uuid import uuid4

from app.search.product_index import ProductSearchIndex


class TestProductSearchIndex:
    def test_search_by_sku(self):
        index = ProductSearchIndex()
        pid = uuid4()
        index.index_product(product_id=pid, sku="SKU-001", name="Widget", category="Tools")
        results = index.search("SKU-001")
        assert len(results) == 1
        assert results[0].product_id == pid

    def test_empty_query(self):
        index = ProductSearchIndex()
        assert index.search("") == []
