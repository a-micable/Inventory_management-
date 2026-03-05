"""Seed demo tenant with sample data for development."""

from __future__ import annotations

import asyncio
import logging

from app.core.enums import UserRole
from app.core.security import hash_password
from app.database import session_scope
from app.models.tenant import Tenant
from app.models.user import User
from app.models.warehouse import Warehouse
from app.repositories.product_repository import ProductRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.repositories.warehouse_repository import WarehouseRepository

logger = logging.getLogger(__name__)


async def seed() -> None:
    async with session_scope() as db:
        tenant_repo = TenantRepository(db)
        existing = await tenant_repo.get_by_slug("demo")
        if existing:
            logger.info("Demo tenant already exists, skipping seed")
            return

        tenant = await tenant_repo.create(name="Demo Corp", slug="demo")
        user_repo = UserRepository(db)
        await user_repo.create(
            tenant_id=tenant.id,
            email="admin@demo.com",
            hashed_password=hash_password("Admin123!"),
            full_name="Demo Admin",
            role=UserRole.ADMIN,
        )
        await user_repo.create(
            tenant_id=tenant.id,
            email="manager@demo.com",
            hashed_password=hash_password("Manager123!"),
            full_name="Demo Manager",
            role=UserRole.MANAGER,
        )

        wh_repo = WarehouseRepository(db)
        main_wh = await wh_repo.create(
            tenant_id=tenant.id,
            name="Main Distribution Center",
            code="WH-MAIN",
            address="100 Industrial Blvd",
            city="Chicago",
            country="US",
        )
        await wh_repo.create(
            tenant_id=tenant.id,
            name="West Coast Hub",
            code="WH-WEST",
            address="2500 Harbor Way",
            city="Los Angeles",
            country="US",
        )

        product_repo = ProductRepository(db)
        products = [
            ("SKU-001", "Wireless Mouse", "Electronics", 29.99),
            ("SKU-002", "Mechanical Keyboard", "Electronics", 89.99),
            ("SKU-003", "USB-C Hub", "Accessories", 45.00),
            ("SKU-004", "Monitor Stand", "Furniture", 59.99),
            ("SKU-005", "Desk Lamp", "Furniture", 34.50),
        ]
        for sku, name, category, price in products:
            await product_repo.create(
                tenant_id=tenant.id,
                sku=sku,
                name=name,
                category=category,
                unit_price=price,
                reorder_point=10,
            )

        logger.info("Demo data seeded for tenant %s (warehouse %s)", tenant.slug, main_wh.code)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())
