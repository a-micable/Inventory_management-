"""Sequential number generation for orders and transfers."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone


def generate_order_number(prefix: str = "ORD") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = secrets.token_hex(3).upper()
    return f"{prefix}-{ts}-{suffix}"


def generate_transfer_number(prefix: str = "TRF") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = secrets.token_hex(3).upper()
    return f"{prefix}-{ts}-{suffix}"


def generate_reservation_ref() -> str:
    return f"RSV-{secrets.token_hex(4).upper()}"
