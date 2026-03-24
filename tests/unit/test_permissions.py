"""Unit tests for RBAC permissions."""

from __future__ import annotations

import pytest

from app.core.enums import UserRole
from app.core.exceptions import AuthorizationError
from app.core.permissions import has_permission, require_permission, role_at_least


class TestPermissions:
    def test_admin_has_all_permissions(self):
        assert has_permission(UserRole.ADMIN, "users:write")
        assert has_permission(UserRole.ADMIN, "audit:read")

    def test_employee_cannot_write_users(self):
        assert not has_permission(UserRole.EMPLOYEE, "users:write")

    def test_employee_can_create_orders(self):
        assert has_permission(UserRole.EMPLOYEE, "orders:create")

    def test_require_permission_raises(self):
        with pytest.raises(AuthorizationError):
            require_permission(UserRole.EMPLOYEE, "audit:read")

    def test_role_hierarchy(self):
        assert role_at_least(UserRole.ADMIN, UserRole.MANAGER)
        assert role_at_least(UserRole.MANAGER, UserRole.EMPLOYEE)
        assert not role_at_least(UserRole.EMPLOYEE, UserRole.MANAGER)
