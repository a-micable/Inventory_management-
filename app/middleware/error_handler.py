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
