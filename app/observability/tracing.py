"""Distributed tracing helpers (OpenTelemetry-ready)."""

from __future__ import annotations

import logging
from contextvars import ContextVar
from uuid import uuid4

logger = logging.getLogger(__name__)

_trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)


def start_trace() -> str:
    trace_id = str(uuid4())
    _trace_id.set(trace_id)
    return trace_id


def get_trace_id() -> str | None:
    return _trace_id.get()


def log_with_trace(message: str, **kwargs) -> None:
    extra = {"trace_id": get_trace_id(), **kwargs}
    logger.info(message, extra=extra)
