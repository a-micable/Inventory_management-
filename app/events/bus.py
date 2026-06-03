"""Simple in-process event bus for domain event dispatch."""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from app.domain.events import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], Any]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed handler %s to %s", handler.__name__, event_type.__name__)

    def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception("Event handler %s failed for %s", handler.__name__, type(event).__name__)

    def clear(self) -> None:
        self._handlers.clear()


event_bus = EventBus()
