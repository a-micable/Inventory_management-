"""Outbound webhook delivery for inventory events."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WebhookPayload:
    event_type: str
    tenant_id: UUID
    entity_id: UUID
    data: dict


class WebhookDispatcher:
    def __init__(self, *, secret: str | None = None, timeout: float = 10.0) -> None:
        self.secret = secret
        self.timeout = timeout

    def _sign(self, body: bytes) -> str | None:
        if not self.secret:
            return None
        return hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()

    async def dispatch(self, url: str, payload: WebhookPayload) -> bool:
        body = json.dumps({
            "event_type": payload.event_type,
            "tenant_id": str(payload.tenant_id),
            "entity_id": str(payload.entity_id),
            "data": payload.data,
        }).encode()
        headers = {"Content-Type": "application/json"}
        signature = self._sign(body)
        if signature:
            headers["X-Webhook-Signature"] = signature

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, content=body, headers=headers)
                response.raise_for_status()
                logger.info("Webhook delivered to %s: %s", url, payload.event_type)
                return True
        except httpx.HTTPError as exc:
            logger.error("Webhook delivery failed to %s: %s", url, exc)
            return False
