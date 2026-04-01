"""Unit tests for webhook dispatcher."""

from __future__ import annotations

from uuid import uuid4

from app.integrations.webhook import WebhookDispatcher, WebhookPayload


class TestWebhookDispatcher:
    def test_sign_without_secret(self):
        dispatcher = WebhookDispatcher()
        assert dispatcher._sign(b"test") is None

    def test_sign_with_secret(self):
        dispatcher = WebhookDispatcher(secret="mysecret")
        sig = dispatcher._sign(b"test")
        assert sig is not None
        assert len(sig) == 64
