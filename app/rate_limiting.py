"""Rate limiting configuration helpers."""

from __future__ import annotations

RATE_LIMITS = {
    "auth_register": "5/minute",
    "auth_login": "10/minute",
    "default": "100/minute",
    "reports": "20/minute",
}


def get_limit(endpoint: str) -> str:
    return RATE_LIMITS.get(endpoint, RATE_LIMITS["default"])
