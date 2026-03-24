"""Unit tests for notification templates."""

from __future__ import annotations

from app.notifications.templates import (
    low_stock_template,
    order_fulfilled_template,
    welcome_template,
)


class TestTemplates:
    def test_low_stock(self):
        msg = low_stock_template("SKU-001", "WH-MAIN", 5, 10)
        assert "SKU-001" in msg
        assert "5" in msg

    def test_welcome(self):
        msg = welcome_template("Acme", "admin@acme.com")
        assert "Acme" in msg
