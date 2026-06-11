"""Generate FastAPI dependency injection modules."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "app/dependencies/__init__.py": '"""FastAPI dependency providers."""\n',
        "app/dependencies/auth.py": _AUTH,
        "app/dependencies/rate_limit.py": _RATE_LIMIT,
        "app/dependencies/services.py": _SERVICES,
    }


_AUTH = '''
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
'''

_RATE_LIMIT = '''
"""Rate limiting configuration."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
'''

_SERVICES = '''
"""Service layer dependency factories."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.report_service import ReportService
from app.services.transfer_service import TransferService
from app.services.user_service import UserService
from app.services.warehouse_service import WarehouseService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


def get_warehouse_service(db: AsyncSession = Depends(get_db)) -> WarehouseService:
    return WarehouseService(db)


def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(db)


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)


def get_transfer_service(db: AsyncSession = Depends(get_db)) -> TransferService:
    return TransferService(db)


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)
'''
