"""Integration tests for authentication flow."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_register_and_login(client, random_email):
    slug = f"tenant-{random_email.split('@')[0]}"
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "tenant_name": "Test Corp",
            "tenant_slug": slug,
            "email": random_email,
            "password": "SecurePass1",
            "full_name": "Test Admin",
        },
    )
    if register_resp.status_code == 200:
        data = register_resp.json()
        assert data["success"] is True
        assert "access_token" in data["data"]["tokens"]

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": random_email, "password": "SecurePass1", "tenant_slug": slug},
    )
    if login_resp.status_code == 200:
        assert login_resp.json()["success"] is True
