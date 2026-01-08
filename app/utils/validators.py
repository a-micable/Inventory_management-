"""Input validation helpers."""

from __future__ import annotations

import re

from app.core.constants import MIN_PASSWORD_LENGTH
from app.core.exceptions import ValidationError

SKU_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9\-_.]{2,63}$")


def validate_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain a lowercase letter")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain a digit")


def validate_sku(sku: str) -> str:
    normalized = sku.strip().upper()
    if not SKU_PATTERN.match(normalized):
        raise ValidationError("Invalid SKU format")
    return normalized
