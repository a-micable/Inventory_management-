"""Unit tests for transfer schemas."""

from __future__ import annotations

from uuid import uuid4

from app.schemas.transfer import TransferCreate, TransferLineCreate


class TestTransferSchemas:
    def test_transfer_create(self):
        t = TransferCreate(
            source_warehouse_id=uuid4(),
            destination_warehouse_id=uuid4(),
            lines=[TransferLineCreate(product_id=uuid4(), quantity=5)],
        )
        assert len(t.lines) == 1
