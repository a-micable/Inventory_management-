"""Domain events for inventory and order lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.utils.datetime_utils import utc_now


@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)
    tenant_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass(frozen=True, slots=True)
class StockAdjustedEvent(DomainEvent):
    inventory_item_id: UUID = field(default_factory=lambda: UUID(int=0))
    product_id: UUID = field(default_factory=lambda: UUID(int=0))
    warehouse_id: UUID = field(default_factory=lambda: UUID(int=0))
    quantity_before: int = 0
    quantity_after: int = 0
    adjustment_type: str = ""


@dataclass(frozen=True, slots=True)
class OrderCreatedEvent(DomainEvent):
    order_id: UUID = field(default_factory=lambda: UUID(int=0))
    order_number: str = ""
    customer_name: str = ""
    item_count: int = 0


@dataclass(frozen=True, slots=True)
class OrderFulfilledEvent(DomainEvent):
    order_id: UUID = field(default_factory=lambda: UUID(int=0))
    order_number: str = ""
    fulfilled_by_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class OrderCancelledEvent(DomainEvent):
    order_id: UUID = field(default_factory=lambda: UUID(int=0))
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class TransferCompletedEvent(DomainEvent):
    transfer_id: UUID = field(default_factory=lambda: UUID(int=0))
    transfer_number: str = ""
    line_count: int = 0


@dataclass(frozen=True, slots=True)
class LowStockAlertEvent(DomainEvent):
    product_id: UUID = field(default_factory=lambda: UUID(int=0))
    sku: str = ""
    warehouse_id: UUID = field(default_factory=lambda: UUID(int=0))
    current_quantity: int = 0
    reorder_point: int = 0
