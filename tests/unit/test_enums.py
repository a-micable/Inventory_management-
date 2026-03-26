"""Unit tests for domain enums."""

from __future__ import annotations

from app.core.enums import AuditAction, OrderStatus, UserRole


class TestEnums:
    def test_user_roles(self):
        assert UserRole.ADMIN.value == "admin"
        assert len(UserRole) == 3

    def test_order_status_transitions(self):
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.FULFILLED.value == "fulfilled"

    def test_audit_actions(self):
        assert AuditAction.ADJUST.value == "adjust"
        assert AuditAction.FULFILL.value == "fulfill"
