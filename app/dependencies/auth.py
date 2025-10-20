"""Authentication dependencies."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.exceptions import AuthenticationError
from app.core.security import decode_token
from app.core.tenant_context import set_current_user_id, set_tenant_context, TenantContext
from app.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise AuthenticationError("Missing authorization header")
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    user_id = UUID(payload["sub"])
    tenant_id = UUID(payload["tenant_id"])
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active or user.tenant_id != tenant_id:
        raise AuthenticationError("User not found or inactive")

    set_tenant_context(TenantContext(tenant_id=tenant_id, tenant_slug=""))
    set_current_user_id(user.id)
    return user


def require_roles(*roles: UserRole):
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            from app.core.exceptions import AuthorizationError
            raise AuthorizationError(f"Requires one of: {[r.value for r in roles]}")
        return user
    return checker
