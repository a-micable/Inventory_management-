"""Integration tests for product CRUD."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
