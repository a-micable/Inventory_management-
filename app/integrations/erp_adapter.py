"""ERP system adapter interface for external inventory sync."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ERPProduct:
    external_id: str
    sku: str
    name: str
    quantity: int
    warehouse_code: str


@dataclass(frozen=True, slots=True)
class ERPSyncResult:
    created: int = 0
    updated: int = 0
    errors: int = 0


class ERPAdapter(ABC):
    @abstractmethod
    async def fetch_products(self, tenant_id: UUID) -> list[ERPProduct]:
        ...

    @abstractmethod
    async def push_order(self, tenant_id: UUID, order_id: UUID) -> bool:
        ...


class MockERPAdapter(ERPAdapter):
    """Mock adapter for development and testing."""

    async def fetch_products(self, tenant_id: UUID) -> list[ERPProduct]:
        logger.info("Mock ERP: fetching products for tenant %s", tenant_id)
        return []

    async def push_order(self, tenant_id: UUID, order_id: UUID) -> bool:
        logger.info("Mock ERP: pushing order %s for tenant %s", order_id, tenant_id)
        return True
