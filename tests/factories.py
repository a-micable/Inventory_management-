"""Test data factories."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from app.core.enums import UserRole
from app.core.security import hash_password


def make_register_payload(
    *,
    tenant_slug: str | None = None,
    email: str | None = None,
) -> dict:
    slug = tenant_slug or f"tenant-{uuid4().hex[:8]}"
    return {
        "tenant_name": f"Test {slug}",
        "tenant_slug": slug,
        "email": email or f"admin-{uuid4().hex[:6]}@test.com",
        "password": "SecurePass1",
        "full_name": "Test Admin",
    }


def make_product_payload(sku: str | None = None) -> dict:
    return {
        "sku": sku or f"SKU-{uuid4().hex[:6].upper()}",
        "name": "Test Product",
        "category": "Test",
        "unit_price": str(Decimal("19.99")),
        "reorder_point": 5,
    }


def make_warehouse_payload(code: str | None = None) -> dict:
    return {
        "name": "Test Warehouse",
        "code": code or f"WH-{uuid4().hex[:4].upper()}",
        "city": "Test City",
        "country": "US",
    }


USER_DEFAULTS = {
    "role": UserRole.EMPLOYEE,
    "password": "SecurePass1",
    "hashed_password": hash_password("SecurePass1"),
}
