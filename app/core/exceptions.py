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
