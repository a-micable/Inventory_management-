"""Unit tests for security module."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("SecurePass1")
        assert hashed != "SecurePass1"
        assert verify_password("SecurePass1", hashed)
        assert not verify_password("WrongPass1", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("SecurePass1")
        h2 = hash_password("SecurePass1")
        assert h1 != h2


class TestJWTTokens:
    def test_access_token_roundtrip(self):
        tenant_id = uuid4()
        token = create_access_token(subject="user-1", tenant_id=tenant_id, role="admin")
        payload = decode_token(token)
        assert payload["sub"] == "user-1"
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_refresh_token_type(self):
        tenant_id = uuid4()
        token = create_refresh_token(subject="user-1", tenant_id=tenant_id)
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_invalid_token_raises(self):
        with pytest.raises(AuthenticationError):
            decode_token("invalid.token.here")
