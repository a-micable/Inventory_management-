"""Unit tests for event bus."""

from __future__ import annotations

from app.domain.events import OrderCreatedEvent
from app.events.bus import EventBus


class TestEventBus:
    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe(OrderCreatedEvent, lambda e: received.append(e))
        event = OrderCreatedEvent(order_number="ORD-001", customer_name="Test")
        bus.publish(event)
        assert len(received) == 1

    def test_clear_handlers(self):
        bus = EventBus()
        bus.subscribe(OrderCreatedEvent, lambda e: None)
        bus.clear()
        assert len(bus._handlers) == 0
