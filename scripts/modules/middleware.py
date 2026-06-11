"""Generate middleware modules."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "app/middleware/__init__.py": '"""HTTP middleware components."""\n',
        "app/middleware/error_handler.py": _ERROR,
        "app/middleware/logging.py": _LOGGING,
        "app/middleware/tenant.py": _TENANT,
        "app/middleware/audit_context.py": _AUDIT,
    }


_ERROR = '''
"""Global exception handlers."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InsufficientStockError,
    NotFoundError,
    PlatformError,
    TenantError,
    ValidationError,
)
from app.utils.response import error_response

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_404_NOT_FOUND,
            content=error_response(exc.message, code="not_found", details=exc.details),
        )

    @app.exception_handler(AuthenticationError)
    async def auth_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content=error_response(exc.message, code="authentication_error"),
        )

    @app.exception_handler(AuthorizationError)
    async def authz_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_403_FORBIDDEN,
            content=error_response(exc.message, code="authorization_error"),
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_409_CONFLICT,
            content=error_response(exc.message, code="conflict", details=exc.details),
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(exc.message, code="validation_error", details=exc.details),
        )

    @app.exception_handler(InsufficientStockError)
    async def stock_handler(request: Request, exc: InsufficientStockError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_409_CONFLICT,
            content=error_response(exc.message, code="insufficient_stock"),
        )

    @app.exception_handler(TenantError)
    async def tenant_handler(request: Request, exc: TenantError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content=error_response(exc.message, code="tenant_error"),
        )

    @app.exception_handler(PlatformError)
    async def platform_handler(request: Request, exc: PlatformError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content=error_response(exc.message, code="platform_error", details=exc.details),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", extra={"path": request.url.path})
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal server error", code="internal_error"),
        )
'''

_LOGGING = '''
"""Request logging middleware."""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "HTTP %s %s -> %d (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={"request_id": request_id},
        )
        response.headers["X-Request-ID"] = request_id
        return response
'''

_TENANT = '''
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
'''

_AUDIT = '''
"""Audit context middleware for capturing request metadata."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class AuditContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.ip_address = request.client.host if request.client else None
        request.state.user_agent = request.headers.get("User-Agent")
        request.state.correlation_id = getattr(request.state, "request_id", None)
        return await call_next(request)
'''
