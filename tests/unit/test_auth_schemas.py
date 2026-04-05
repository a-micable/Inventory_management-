"""Unit tests for auth schemas."""

from __future__ import annotations

from app.schemas.auth import LoginRequest, RegisterRequest


class TestAuthSchemas:
    def test_register_request(self):
        req = RegisterRequest(
            tenant_name="Acme Corp",
            tenant_slug="acme",
            email="admin@acme.com",
            password="SecurePass1",
            full_name="Admin User",
        )
        assert req.tenant_slug == "acme"

    def test_login_request(self):
        req = LoginRequest(email="user@test.com", password="pass", tenant_slug="demo")
        assert req.tenant_slug == "demo"
