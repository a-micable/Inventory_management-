"""Low stock alert monitoring service."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.events import LowStockAlertEvent
from app.events.bus import event_bus
from app.models.inventory import InventoryItem
from app.models.product import Product

logger = logging.getLogger(__name__)


class StockAlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def check_reorder_points(self, tenant_id: UUID) -> list[LowStockAlertEvent]:
        stmt = (
            select(InventoryItem)
            .join(Product)
            .where(InventoryItem.tenant_id == tenant_id)
            .options(selectinload(InventoryItem.product), selectinload(InventoryItem.warehouse))
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        alerts: list[LowStockAlertEvent] = []

        for item in items:
            if item.product.reorder_point > 0 and item.quantity_on_hand <= item.product.reorder_point:
                event = LowStockAlertEvent(
                    tenant_id=tenant_id,
                    product_id=item.product_id,
                    sku=item.product.sku,
                    warehouse_id=item.warehouse_id,
                    current_quantity=item.quantity_on_hand,
                    reorder_point=item.product.reorder_point,
                )
                alerts.append(event)
                event_bus.publish(event)

        logger.info("Found %d low stock alerts for tenant %s", len(alerts), tenant_id)
        return alerts
