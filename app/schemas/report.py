"""Report generation schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class InventoryReportRequest(BaseModel):
    warehouse_id: UUID | None = None
    category: str | None = None
    include_zero_stock: bool = False


class InventoryReportRow(BaseModel):
    product_id: UUID
    sku: str
    product_name: str
    warehouse_id: UUID
    warehouse_code: str
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    reorder_point: int
    below_reorder: bool
    unit_price: Decimal
    stock_value: Decimal


class InventoryReportResponse(BaseModel):
    generated_at: datetime
    total_skus: int
    total_stock_value: Decimal
    rows: list[InventoryReportRow]


class SalesReportRequest(BaseModel):
    start_date: date
    end_date: date
    warehouse_id: UUID | None = None


class SalesReportRow(BaseModel):
    order_id: UUID
    order_number: str
    fulfilled_at: datetime
    customer_name: str
    warehouse_id: UUID
    line_count: int
    subtotal: Decimal


class SalesReportResponse(BaseModel):
    generated_at: datetime
    period_start: date
    period_end: date
    total_orders: int
    total_revenue: Decimal
    rows: list[SalesReportRow]


class ReportJobResponse(BaseModel):
    id: UUID
    report_type: str
    status: str
    created_at: datetime
    result: dict | None = None
    error_message: str | None = None
