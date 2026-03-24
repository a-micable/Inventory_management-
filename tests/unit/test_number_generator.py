"""Unit tests for number generators."""

from __future__ import annotations

import re

from app.services.number_generator import (
    generate_order_number,
    generate_reservation_ref,
    generate_transfer_number,
)


class TestNumberGenerators:
    def test_order_number_format(self):
        num = generate_order_number()
        assert re.match(r"ORD-\d{8}-[A-F0-9]{6}", num)

    def test_transfer_number_format(self):
        num = generate_transfer_number()
        assert num.startswith("TRF-")

    def test_reservation_ref_unique(self):
        refs = {generate_reservation_ref() for _ in range(100)}
        assert len(refs) == 100
