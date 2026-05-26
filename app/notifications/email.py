"""Email notification service (stub for production SMTP integration)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class EmailMessage:
    to: str
    subject: str
    body: str
    html_body: str | None = None


class EmailService:
    def __init__(self, *, smtp_host: str | None = None, smtp_port: int = 587) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    async def send(self, message: EmailMessage) -> bool:
        if not self.smtp_host:
            logger.info("Email (dry-run): to=%s subject=%s", message.to, message.subject)
            return True
        logger.info("Sending email to %s: %s", message.to, message.subject)
        return True

    async def send_low_stock_alert(self, *, to: str, sku: str, warehouse: str, qty: int) -> bool:
        return await self.send(
            EmailMessage(
                to=to,
                subject=f"Low Stock Alert: {sku}",
                body=f"Product {sku} at {warehouse} has only {qty} units remaining.",
            )
        )

    async def send_order_confirmation(self, *, to: str, order_number: str, total: str) -> bool:
        return await self.send(
            EmailMessage(
                to=to,
                subject=f"Order Confirmation: {order_number}",
                body=f"Your order {order_number} has been confirmed. Total: {total}",
            )
        )
