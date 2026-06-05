"""Custom business metrics for Prometheus."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Gauge, Histogram

    ORDERS_CREATED = Counter(
        "inventory_orders_created_total",
        "Total orders created",
        ["tenant_id", "status"],
    )
    STOCK_ADJUSTMENTS = Counter(
        "inventory_stock_adjustments_total",
        "Total stock adjustments",
        ["tenant_id", "type"],
    )
    ACTIVE_RESERVATIONS = Gauge(
        "inventory_active_reservations",
        "Current active stock reservations",
        ["tenant_id"],
    )
    REPORT_GENERATION_SECONDS = Histogram(
        "inventory_report_generation_seconds",
        "Report generation duration",
        ["report_type"],
    )
except ImportError:
    logger.warning("prometheus_client not available for custom metrics")
