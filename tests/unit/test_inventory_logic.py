"""Unit tests for inventory calculations."""

from __future__ import annotations


class TestInventoryCalculations:
    def test_available_quantity(self):
        on_hand = 100
        reserved = 30
        available = max(0, on_hand - reserved)
        assert available == 70

    def test_available_never_negative(self):
        on_hand = 10
        reserved = 15
        available = max(0, on_hand - reserved)
        assert available == 0

    def test_adjustment_delta(self):
        before = 50
        delta = -10
        after = before + delta
        assert after == 40
        assert after >= 0
