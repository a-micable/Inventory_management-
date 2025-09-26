"""Data export service for CSV/JSON inventory dumps."""

from __future__ import annotations

import csv
import io
import json
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.inventory_repo = InventoryRepository(session)
        self.product_repo = ProductRepository(session)

    async def export_inventory_csv(self, tenant_id: UUID, *, warehouse_id: UUID | None = None) -> str:
        items = await self.inventory_repo.list_by_tenant(tenant_id, warehouse_id=warehouse_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["product_id", "warehouse_id", "on_hand", "reserved", "available"])
        for item in items:
            writer.writerow([
                str(item.product_id),
                str(item.warehouse_id),
                item.quantity_on_hand,
                item.quantity_reserved,
                item.quantity_available,
            ])
        return output.getvalue()

    async def export_products_json(self, tenant_id: UUID) -> str:
        products = await self.product_repo.list_by_tenant(tenant_id, limit=10000)
        data = [
            {
                "id": str(p.id),
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "unit_price": str(p.unit_price),
                "reorder_point": p.reorder_point,
            }
            for p in products
        ]
        return json.dumps(data, indent=2)
