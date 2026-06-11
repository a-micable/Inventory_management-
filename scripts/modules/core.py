"""Generate core application modules."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "app/__init__.py": '"""Multi-Tenant Inventory & Order Management Platform."""\n\n__version__ = "1.0.0"\n',
        "app/config.py": _CONFIG,
        "app/database.py": _DATABASE,
        "app/logging_config.py": _LOGGING,
        "app/main.py": _MAIN,
        "app/health.py": _HEALTH,
        "app/metrics.py": _METRICS,
        "app/core/__init__.py": '"""Core utilities and cross-cutting concerns."""\n',
        "app/core/enums.py": _ENUMS,
        "app/core/constants.py": _CONSTANTS,
        "app/core/exceptions.py": _EXCEPTIONS,
        "app/core/security.py": _SECURITY,
        "app/core/permissions.py": _PERMISSIONS,
        "app/core/tenant_context.py": _TENANT_CONTEXT,
        "app/core/cache.py": _CACHE,
        "app/cli/__init__.py": "",
        "app/cli/seed_demo.py": _SEED_DEMO,
        "app/cli/manage.py": _MANAGE,
        "app/utils/__init__.py": '"""Shared utility functions."""\n',
        "app/utils/pagination.py": _PAGINATION,
        "app/utils/datetime_utils.py": _DATETIME_UTILS,
        "app/utils/uuid.py": _UUID_UTILS,
        "app/utils/response.py": _RESPONSE,
        "app/utils/validators.py": _VALIDATORS,
    }


_CONFIG = '''
"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("Inventory Platform API", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")

    database_url: str = Field(..., env="DATABASE_URL")
    sync_database_url: str = Field(..., env="SYNC_DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    celery_broker_url: str = Field("redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field("redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES", ge=5)
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS", ge=1)

    allowed_origins: list[str] = Field(default_factory=list, env="ALLOWED_ORIGINS")
    run_migrations: bool = Field(False, env="RUN_MIGRATIONS")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    default_tenant_slug: str = Field("demo", env="DEFAULT_TENANT_SLUG")

    cache_ttl_seconds: int = Field(300, env="CACHE_TTL_SECONDS", ge=60)
    audit_retention_days: int = Field(365, env="AUDIT_RETENTION_DAYS", ge=30)
    max_page_size: int = Field(100, env="MAX_PAGE_SIZE", ge=10, le=500)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        if isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]
        raise TypeError("ALLOWED_ORIGINS must be comma-separated string or list")


@lru_cache
def get_settings() -> Settings:
    return Settings()
'''

_DATABASE = '''
"""Async SQLAlchemy database session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
'''

_LOGGING = '''
"""Structured JSON logging configuration."""

from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger

from app.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s %(tenant_id)s %(user_id)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )


class TenantLogAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("tenant_id", self.extra.get("tenant_id"))
        extra.setdefault("user_id", self.extra.get("user_id"))
        return msg, kwargs
'''

_MAIN = '''
"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.core.cache import close_redis, init_redis
from app.logging_config import configure_logging
from app.metrics import setup_metrics
from app.middleware.audit_context import AuditContextMiddleware
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.tenant import TenantResolutionMiddleware
from app.health import router as health_router
from app.routers import (
    audit,
    auth,
    inventory,
    orders,
    products,
    reports,
    users,
    warehouses,
)

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_redis()
    logger.info("Application startup complete", extra={"version": settings.app_version})
    yield
    await close_redis()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-Tenant Inventory & Order Management Platform",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AuditContextMiddleware)
    app.add_middleware(TenantResolutionMiddleware)

    register_exception_handlers(app)
    setup_metrics(app)

    from app.dependencies.rate_limit import limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.include_router(health_router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(products.router, prefix="/api/v1")
    app.include_router(inventory.router, prefix="/api/v1")
    app.include_router(warehouses.router, prefix="/api/v1")
    app.include_router(orders.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")
    app.include_router(audit.router, prefix="/api/v1")

    return app


app = create_app()
'''

_HEALTH = '''
"""Health and readiness probe endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.cache import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    redis = await get_redis()
    await redis.ping()
    return {"status": "ready", "database": "ok", "redis": "ok"}
'''

_METRICS = '''
"""Prometheus metrics instrumentation."""

from __future__ import annotations

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app: FastAPI) -> None:
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/health", "/ready", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
'''

_ENUMS = '''
"""Domain enumerations used across the platform."""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class StockAdjustmentType(str, enum.Enum):
    RECEIPT = "receipt"
    DAMAGE = "damage"
    CORRECTION = "correction"
    RETURN = "return"
    CYCLE_COUNT = "cycle_count"


class ReservationStatus(str, enum.Enum):
    ACTIVE = "active"
    RELEASED = "released"
    CONSUMED = "consumed"
    EXPIRED = "expired"


class TransferStatus(str, enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ADJUST = "adjust"
    RESERVE = "reserve"
    RELEASE = "release"
    TRANSFER = "transfer"
    FULFILL = "fulfill"
    CANCEL = "cancel"
    LOGIN = "login"
    REGISTER = "register"


class AuditEntityType(str, enum.Enum):
    USER = "user"
    PRODUCT = "product"
    INVENTORY = "inventory"
    ORDER = "order"
    WAREHOUSE = "warehouse"
    TRANSFER = "transfer"
    RESERVATION = "reservation"
    REPORT = "report"
'''

_CONSTANTS = '''
"""Application-wide constants."""

from __future__ import annotations

DEFAULT_CURRENCY = "USD"
DEFAULT_TIMEZONE = "UTC"
MIN_PASSWORD_LENGTH = 8
MAX_SKU_LENGTH = 64
MAX_PRODUCT_NAME_LENGTH = 255
ORDER_NUMBER_PREFIX = "ORD"
TRANSFER_NUMBER_PREFIX = "TRF"
RESERVATION_TTL_HOURS = 24
REPORT_CACHE_PREFIX = "report:"
INVENTORY_CACHE_PREFIX = "inventory:"
PRODUCT_CACHE_PREFIX = "product:"
'''

_EXCEPTIONS = '''
"""Custom exception hierarchy for domain errors."""

from __future__ import annotations

from typing import Any


class PlatformError(Exception):
    """Base exception for all platform errors."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(PlatformError):
    """Resource not found."""


class ConflictError(PlatformError):
    """Resource conflict (duplicate, stale state)."""


class ValidationError(PlatformError):
    """Business rule validation failure."""


class AuthorizationError(PlatformError):
    """Insufficient permissions."""


class AuthenticationError(PlatformError):
    """Invalid or missing credentials."""


class InsufficientStockError(PlatformError):
    """Not enough inventory to fulfill operation."""


class TenantError(PlatformError):
    """Tenant resolution or isolation failure."""
'''

_SECURITY = '''
"""JWT token creation, validation, and password hashing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.core.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    *,
    subject: str,
    tenant_id: UUID,
    role: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "tenant_id": str(tenant_id),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(*, subject: str, tenant_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": subject,
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc
'''

_PERMISSIONS = '''
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
'''

_TENANT_CONTEXT = '''
"""Request-scoped tenant context using contextvars."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import TenantError


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: UUID
    tenant_slug: str


_current_tenant: ContextVar[TenantContext | None] = ContextVar("current_tenant", default=None)
_current_user_id: ContextVar[UUID | None] = ContextVar("current_user_id", default=None)


def set_tenant_context(ctx: TenantContext) -> None:
    _current_tenant.set(ctx)


def get_tenant_context() -> TenantContext:
    ctx = _current_tenant.get()
    if ctx is None:
        raise TenantError("Tenant context not established for this request")
    return ctx


def get_tenant_id() -> UUID:
    return get_tenant_context().tenant_id


def set_current_user_id(user_id: UUID | None) -> None:
    _current_user_id.set(user_id)


def get_current_user_id() -> UUID | None:
    return _current_user_id.get()


def clear_context() -> None:
    _current_tenant.set(None)
    _current_user_id.set(None)
'''

_CACHE = '''
"""Redis cache client and helpers."""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis: aioredis.Redis | None = None


async def init_redis() -> None:
    global _redis
    _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await _redis.ping()
    logger.info("Redis connection established")


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def get_redis() -> aioredis.Redis:
    if _redis is None:
        await init_redis()
    assert _redis is not None
    return _redis


async def cache_get(key: str) -> Any | None:
    redis = await get_redis()
    raw = await redis.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    redis = await get_redis()
    serialized = json.dumps(value, default=str)
    await redis.set(key, serialized, ex=ttl or settings.cache_ttl_seconds)


async def cache_delete(key: str) -> None:
    redis = await get_redis()
    await redis.delete(key)


async def cache_delete_pattern(pattern: str) -> int:
    redis = await get_redis()
    deleted = 0
    async for key in redis.scan_iter(match=pattern):
        await redis.delete(key)
        deleted += 1
    return deleted
'''

_SEED_DEMO = '''
"""Seed demo tenant with sample data for development."""

from __future__ import annotations

import asyncio
import logging

from app.core.enums import UserRole
from app.core.security import hash_password
from app.database import session_scope
from app.models.tenant import Tenant
from app.models.user import User
from app.models.warehouse import Warehouse
from app.repositories.product_repository import ProductRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.repositories.warehouse_repository import WarehouseRepository

logger = logging.getLogger(__name__)


async def seed() -> None:
    async with session_scope() as db:
        tenant_repo = TenantRepository(db)
        existing = await tenant_repo.get_by_slug("demo")
        if existing:
            logger.info("Demo tenant already exists, skipping seed")
            return

        tenant = await tenant_repo.create(name="Demo Corp", slug="demo")
        user_repo = UserRepository(db)
        await user_repo.create(
            tenant_id=tenant.id,
            email="admin@demo.com",
            hashed_password=hash_password("Admin123!"),
            full_name="Demo Admin",
            role=UserRole.ADMIN,
        )
        await user_repo.create(
            tenant_id=tenant.id,
            email="manager@demo.com",
            hashed_password=hash_password("Manager123!"),
            full_name="Demo Manager",
            role=UserRole.MANAGER,
        )

        wh_repo = WarehouseRepository(db)
        main_wh = await wh_repo.create(
            tenant_id=tenant.id,
            name="Main Distribution Center",
            code="WH-MAIN",
            address="100 Industrial Blvd",
            city="Chicago",
            country="US",
        )
        await wh_repo.create(
            tenant_id=tenant.id,
            name="West Coast Hub",
            code="WH-WEST",
            address="2500 Harbor Way",
            city="Los Angeles",
            country="US",
        )

        product_repo = ProductRepository(db)
        products = [
            ("SKU-001", "Wireless Mouse", "Electronics", 29.99),
            ("SKU-002", "Mechanical Keyboard", "Electronics", 89.99),
            ("SKU-003", "USB-C Hub", "Accessories", 45.00),
            ("SKU-004", "Monitor Stand", "Furniture", 59.99),
            ("SKU-005", "Desk Lamp", "Furniture", 34.50),
        ]
        for sku, name, category, price in products:
            await product_repo.create(
                tenant_id=tenant.id,
                sku=sku,
                name=name,
                category=category,
                unit_price=price,
                reorder_point=10,
            )

        logger.info("Demo data seeded for tenant %s (warehouse %s)", tenant.slug, main_wh.code)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())
'''

_MANAGE = '''
"""CLI management commands."""

from __future__ import annotations

import argparse
import asyncio
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory Platform management CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("seed", help="Seed demo tenant data")

    args = parser.parse_args()
    if args.command == "seed":
        from app.cli.seed_demo import seed
        asyncio.run(seed())
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
'''

_PAGINATION = '''
"""Pagination helpers for list endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Generic, Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class PageParams:
    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if self.page_size < 1:
            raise ValueError("page_size must be >= 1")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.total == 0:
            return 0
        return ceil(self.total / self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1
'''

_DATETIME_UTILS = '''
"""Datetime utility functions."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
'''

_UUID_UTILS = '''
"""UUID generation and parsing helpers."""

from __future__ import annotations

from uuid import UUID, uuid4


def generate_uuid() -> UUID:
    return uuid4()


def parse_uuid(value: str) -> UUID:
    return UUID(value)
'''

_RESPONSE = '''
"""Standardized API response helpers."""

from __future__ import annotations

from typing import Any


def success_response(data: Any, *, message: str = "OK") -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}


def error_response(message: str, *, code: str = "error", details: dict | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"success": False, "message": message, "code": code}
    if details:
        payload["details"] = details
    return payload
'''

_VALIDATORS = '''
"""Input validation helpers."""

from __future__ import annotations

import re

from app.core.constants import MIN_PASSWORD_LENGTH
from app.core.exceptions import ValidationError

SKU_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9\-_.]{2,63}$")


def validate_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain a lowercase letter")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain a digit")


def validate_sku(sku: str) -> str:
    normalized = sku.strip().upper()
    if not SKU_PATTERN.match(normalized):
        raise ValidationError("Invalid SKU format")
    return normalized
'''
