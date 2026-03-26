"""Unit tests for datetime utilities."""

from __future__ import annotations

from datetime import datetime, timezone

from app.utils.datetime_utils import ensure_utc, utc_now


class TestDatetimeUtils:
    def test_utc_now_is_aware(self):
        now = utc_now()
        assert now.tzinfo is not None

    def test_ensure_utc_naive(self):
        naive = datetime(2025, 1, 1, 12, 0, 0)
        result = ensure_utc(naive)
        assert result.tzinfo == timezone.utc
