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
