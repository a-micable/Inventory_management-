"""Tenant resolution middleware."""

from __future__ import annotations

import logging
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.tenant_context import TenantContext, clear_context, set_tenant_context

logger = logging.getLogger(__name__)

PUBLIC_PATHS = {"/health", "/ready", "/docs", "/redoc", "/openapi.json", "/metrics"}


class TenantResolutionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        tenant_slug = request.headers.get("X-Tenant-Slug")
        tenant_id_header = request.headers.get("X-Tenant-ID")

        if tenant_id_header and tenant_slug:
            try:
                set_tenant_context(
                    TenantContext(tenant_id=UUID(tenant_id_header), tenant_slug=tenant_slug)
                )
            except ValueError:
                logger.warning("Invalid tenant ID header: %s", tenant_id_header)

        try:
            return await call_next(request)
        finally:
            clear_context()
