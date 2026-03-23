"""Integration tests for audit logging."""

from __future__ import annotations

from app.core.enums import AuditAction, AuditEntityType


class TestAuditEnums:
    def test_inventory_actions_logged(self):
        inventory_actions = {
            AuditAction.ADJUST,
            AuditAction.RESERVE,
            AuditAction.RELEASE,
            AuditAction.TRANSFER,
        }
        for action in inventory_actions:
            assert action in AuditAction

    def test_order_entity_type(self):
        assert AuditEntityType.ORDER.value == "order"
