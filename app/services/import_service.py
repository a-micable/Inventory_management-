"""Bulk import service for products and inventory."""

from __future__ import annotations

import csv
import io
import logging
from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.repositories.product_repository import ProductRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.services.inventory_service import InventoryService
from app.schemas.inventory import StockAdjustmentCreate
from app.core.enums import StockAdjustmentType

logger = logging.getLogger(__name__)


class ImportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.product_repo = ProductRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.inventory = InventoryService(session)

    async def import_products_csv(
        self,
        tenant_id: UUID,
        csv_content: str,
        *,
        actor_id: UUID,
        actor_email: str,
    ) -> dict:
        reader = csv.DictReader(io.StringIO(csv_content))
        created = 0
        skipped = 0
        errors: list[str] = []

        for row_num, row in enumerate(reader, start=2):
            try:
                sku = row.get("sku", "").strip().upper()
                name = row.get("name", "").strip()
                if not sku or not name:
                    raise ValidationError("SKU and name are required")
                existing = await self.product_repo.get_by_sku(tenant_id, sku)
                if existing:
                    skipped += 1
                    continue
                price = Decimal(row.get("unit_price", "0"))
                await self.product_repo.create(
                    tenant_id=tenant_id,
                    sku=sku,
                    name=name,
                    category=row.get("category"),
                    unit_price=price,
                    reorder_point=int(row.get("reorder_point", "0")),
                )
                created += 1
            except (ValidationError, InvalidOperation, ValueError) as exc:
                errors.append(f"Row {row_num}: {exc}")

        logger.info("Product import: created=%d skipped=%d errors=%d", created, skipped, len(errors))
        return {"created": created, "skipped": skipped, "errors": errors}

    async def import_stock_csv(
        self,
        tenant_id: UUID,
        csv_content: str,
        *,
        actor_id: UUID,
        actor_email: str,
    ) -> dict:
        reader = csv.DictReader(io.StringIO(csv_content))
        adjusted = 0
        errors: list[str] = []

        for row_num, row in enumerate(reader, start=2):
            try:
                sku = row.get("sku", "").strip().upper()
                wh_code = row.get("warehouse_code", "").strip().upper()
                qty = int(row.get("quantity", "0"))
                product = await self.product_repo.get_by_sku(tenant_id, sku)
                warehouse = await self.warehouse_repo.get_by_code(tenant_id, wh_code)
                if not product or not warehouse:
                    errors.append(f"Row {row_num}: product or warehouse not found")
                    continue
                await self.inventory.adjust_stock(
                    tenant_id,
                    StockAdjustmentCreate(
                        product_id=product.id,
                        warehouse_id=warehouse.id,
                        adjustment_type=StockAdjustmentType.RECEIPT,
                        quantity_delta=qty,
                        reason="Bulk import",
                    ),
                    actor_id=actor_id,
                    actor_email=actor_email,
                    actor_role=None,  # type: ignore[arg-type]
                )
                adjusted += 1
            except (ValueError, ValidationError) as exc:
                errors.append(f"Row {row_num}: {exc}")

        return {"adjusted": adjusted, "errors": errors}
