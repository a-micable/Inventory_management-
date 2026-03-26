"""Unit tests for exception hierarchy."""

from __future__ import annotations

from app.core.exceptions import (
    ConflictError,
    InsufficientStockError,
    NotFoundError,
    PlatformError,
)


class TestExceptions:
    def test_platform_error_details(self):
        exc = PlatformError("test", details={"key": "value"})
        assert exc.message == "test"
        assert exc.details["key"] == "value"

    def test_not_found_inherits_platform(self):
        assert issubclass(NotFoundError, PlatformError)

    def test_insufficient_stock(self):
        exc = InsufficientStockError("no stock")
        assert str(exc) == "no stock"
