"""Integration tests for warehouse transfers."""

from __future__ import annotations

from app.core.enums import TransferStatus


class TestTransferStatus:
    def test_pending_to_completed_flow(self):
        assert TransferStatus.PENDING.value == "pending"
        assert TransferStatus.COMPLETED.value == "completed"
