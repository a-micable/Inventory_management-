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
