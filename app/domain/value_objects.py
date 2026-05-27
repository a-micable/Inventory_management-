"""Immutable value objects for domain modeling."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int) -> Money:
        return Money(self.amount * factor, self.currency)


@dataclass(frozen=True, slots=True)
class SKU:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()
        object.__setattr__(self, "value", normalized)
        if len(normalized) < 3:
            raise ValueError("SKU must be at least 3 characters")


@dataclass(frozen=True, slots=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Quantity cannot be negative")

    def add(self, delta: int) -> Quantity:
        return Quantity(self.value + delta)

    def subtract(self, amount: int) -> Quantity:
        result = self.value - amount
        if result < 0:
            raise ValueError("Insufficient quantity")
        return Quantity(result)


@dataclass(frozen=True, slots=True)
class TenantId:
    value: UUID


@dataclass(frozen=True, slots=True)
class OrderNumber:
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Address:
    street: str | None
    city: str | None
    country: str | None

    @property
    def formatted(self) -> str:
        parts = [p for p in (self.street, self.city, self.country) if p]
        return ", ".join(parts) if parts else "N/A"
