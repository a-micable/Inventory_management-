"""Event handlers for side effects (notifications, cache invalidation)."""

from __future__ import annotations

import logging

from app.core.cache import cache_delete_pattern
from app.core.constants import INVENTORY_CACHE_PREFIX, PRODUCT_CACHE_PREFIX
from app.domain.events import (
    LowStockAlertEvent,
    OrderCreatedEvent,
    OrderFulfilledEvent,
    StockAdjustedEvent,
    TransferCompletedEvent,
)

logger = logging.getLogger(__name__)


async def on_stock_adjusted(event: StockAdjustedEvent) -> None:
    await cache_delete_pattern(f"{INVENTORY_CACHE_PREFIX}{event.tenant_id}:*")
    logger.info(
        "Stock adjusted: product=%s warehouse=%s %d -> %d",
        event.product_id,
        event.warehouse_id,
        event.quantity_before,
        event.quantity_after,
    )


def on_order_created(event: OrderCreatedEvent) -> None:
    logger.info(
        "Order created: %s for %s (%d items)",
        event.order_number,
        event.customer_name,
        event.item_count,
    )


def on_order_fulfilled(event: OrderFulfilledEvent) -> None:
    logger.info("Order fulfilled: %s", event.order_number)


async def on_transfer_completed(event: TransferCompletedEvent) -> None:
    await cache_delete_pattern(f"{INVENTORY_CACHE_PREFIX}{event.tenant_id}:*")
    logger.info("Transfer completed: %s (%d lines)", event.transfer_number, event.line_count)


def on_low_stock_alert(event: LowStockAlertEvent) -> None:
    logger.warning(
        "LOW STOCK: SKU=%s warehouse=%s qty=%d reorder=%d",
        event.sku,
        event.warehouse_id,
        event.current_quantity,
        event.reorder_point,
    )


def register_handlers(bus) -> None:
    bus.subscribe(StockAdjustedEvent, lambda e: None)  # sync placeholder
    bus.subscribe(OrderCreatedEvent, on_order_created)
    bus.subscribe(OrderFulfilledEvent, on_order_fulfilled)
    bus.subscribe(TransferCompletedEvent, lambda e: None)
    bus.subscribe(LowStockAlertEvent, on_low_stock_alert)
