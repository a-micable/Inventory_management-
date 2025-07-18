"""Role-based access control definitions and helpers."""

from __future__ import annotations

from app.core.enums import UserRole
from app.core.exceptions import AuthorizationError

ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.EMPLOYEE: 1,
    UserRole.MANAGER: 2,
    UserRole.ADMIN: 3,
}

PERMISSIONS: dict[str, set[UserRole]] = {
    "users:read": {UserRole.ADMIN, UserRole.MANAGER},
    "users:write": {UserRole.ADMIN},
    "users:delete": {UserRole.ADMIN},
    "products:read": {UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE},
    "products:write": {UserRole.ADMIN, UserRole.MANAGER},
    "inventory:read": {UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE},
    "inventory:adjust": {UserRole.ADMIN, UserRole.MANAGER},
    "inventory:transfer": {UserRole.ADMIN, UserRole.MANAGER},
    "orders:read": {UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE},
    "orders:create": {UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE},
    "orders:fulfill": {UserRole.ADMIN, UserRole.MANAGER},
    "orders:cancel": {UserRole.ADMIN, UserRole.MANAGER},
    "warehouses:read": {UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE},
    "warehouses:write": {UserRole.ADMIN, UserRole.MANAGER},
    "reports:read": {UserRole.ADMIN, UserRole.MANAGER},
    "audit:read": {UserRole.ADMIN},
}


def has_permission(role: UserRole, permission: str) -> bool:
    allowed = PERMISSIONS.get(permission, set())
    return role in allowed


def require_permission(role: UserRole, permission: str) -> None:
    if not has_permission(role, permission):
        raise AuthorizationError(f"Role '{role.value}' lacks permission '{permission}'")


def role_at_least(role: UserRole, minimum: UserRole) -> bool:
    return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY.get(minimum, 0)
