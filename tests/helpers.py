"""Test helper utilities."""

from __future__ import annotations

from typing import Any


def assert_success_response(response_data: dict[str, Any]) -> Any:
    assert response_data.get("success") is True
    return response_data.get("data")


def assert_error_response(response_data: dict[str, Any], *, code: str | None = None) -> None:
    assert response_data.get("success") is False
    if code:
        assert response_data.get("code") == code


async def auth_headers(client, register_payload: dict) -> dict[str, str]:
    """Register and return authorization headers."""
    resp = await client.post("/api/v1/auth/register", json=register_payload)
    if resp.status_code != 200:
        return {}
    data = resp.json()["data"]
    token = data["tokens"]["access_token"]
    tenant_id = data["user"]["tenant_id"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id,
        "X-Tenant-Slug": register_payload["tenant_slug"],
    }
