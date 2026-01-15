"""UUID generation and parsing helpers."""

from __future__ import annotations

from uuid import UUID, uuid4


def generate_uuid() -> UUID:
    return uuid4()


def parse_uuid(value: str) -> UUID:
    return UUID(value)
