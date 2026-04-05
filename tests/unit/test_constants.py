"""Unit tests for constants."""

from __future__ import annotations

from app.core.constants import (
    DEFAULT_CURRENCY,
    MIN_PASSWORD_LENGTH,
    ORDER_NUMBER_PREFIX,
    RESERVATION_TTL_HOURS,
)


class TestConstants:
    def test_defaults(self):
        assert DEFAULT_CURRENCY == "USD"
        assert MIN_PASSWORD_LENGTH >= 8
        assert ORDER_NUMBER_PREFIX == "ORD"
        assert RESERVATION_TTL_HOURS == 24
