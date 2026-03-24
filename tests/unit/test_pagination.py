"""Unit tests for pagination."""

from __future__ import annotations

import pytest

from app.utils.pagination import Page, PageParams


class TestPageParams:
    def test_offset_calculation(self):
        params = PageParams(page=3, page_size=20)
        assert params.offset == 40

    def test_invalid_page_raises(self):
        with pytest.raises(ValueError):
            PageParams(page=0)


class TestPage:
    def test_total_pages(self):
        page = Page(items=[1, 2], total=45, page=1, page_size=20)
        assert page.total_pages == 3
        assert page.has_next is True
        assert page.has_previous is False

    def test_empty_page(self):
        page = Page(items=[], total=0, page=1, page_size=20)
        assert page.total_pages == 0
