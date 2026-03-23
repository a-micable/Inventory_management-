"""Integration tests for role-based access control."""

from __future__ import annotations

from app.core.enums import UserRole
from app.core.permissions import PERMISSIONS


class TestRBAC:
    def test_all_roles_have_some_permissions(self):
        all_roles = set(UserRole)
        for perm, roles in PERMISSIONS.items():
            assert roles.issubset(all_roles)

    def test_admin_only_audit(self):
        assert UserRole.ADMIN in PERMISSIONS["audit:read"]
        assert UserRole.EMPLOYEE not in PERMISSIONS["audit:read"]
