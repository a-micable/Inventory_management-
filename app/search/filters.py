"""Query filter builders for search endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class ProductFilters:
    search: str | None = None
    category: str | None = None
    active_only: bool = True
    min_price: float | None = None
    max_price: float | None = None


@dataclass
class OrderFilters:
    status: str | None = None
    warehouse_id: UUID | None = None
    customer_search: str | None = None
    date_from: str | None = None
    date_to: str | None = None


@dataclass
class InventoryFilters:
    warehouse_id: UUID | None = None
    below_reorder: bool = False
    include_zero: bool = False


def build_product_filter_kwargs(filters: ProductFilters) -> dict:
    kwargs = {"active_only": filters.active_only}
    if filters.search:
        kwargs["search"] = filters.search
    if filters.category:
        kwargs["category"] = filters.category
    return kwargs
