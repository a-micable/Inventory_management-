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
