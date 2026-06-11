"""Generate Pydantic schemas."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "app/schemas/__init__.py": '"""Pydantic request/response schemas."""\n',
        "app/schemas/common.py": _COMMON,
        "app/schemas/auth.py": _AUTH,
        "app/schemas/user.py": _USER,
        "app/schemas/product.py": _PRODUCT,
        "app/schemas/warehouse.py": _WAREHOUSE,
        "app/schemas/inventory.py": _INVENTORY,
        "app/schemas/order.py": _ORDER,
        "app/schemas/transfer.py": _TRANSFER,
        "app/schemas/report.py": _REPORT,
        "app/schemas/audit.py": _AUDIT,
    }


_COMMON = '''
"""Shared schema types."""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class IDResponse(BaseModel):
    id: UUID


class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
'''

_AUTH = '''
"""Authentication schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import UserRole
from app.schemas.common import ORMBase


class RegisterRequest(BaseModel):
    tenant_name: str = Field(..., min_length=2, max_length=255)
    tenant_slug: str = Field(..., min_length=2, max_length=64, pattern=r"^[a-z0-9-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str = Field(..., min_length=2, max_length=64)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class AuthUserResponse(ORMBase):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    tenant_id: UUID
'''

_USER = '''
"""User management schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import UserRole
from app.schemas.common import ORMBase, TimestampSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.EMPLOYEE


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(ORMBase, TimestampSchema):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    tenant_id: UUID
'''

_PRODUCT = '''
"""Product catalog schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase, TimestampSchema


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    unit_price: Decimal = Field(..., ge=0)
    reorder_point: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    unit_price: Decimal | None = Field(None, ge=0)
    reorder_point: int | None = Field(None, ge=0)
    is_active: bool | None = None


class ProductResponse(ORMBase, TimestampSchema):
    id: UUID
    sku: str
    name: str
    description: str | None
    category: str | None
    unit_price: Decimal
    reorder_point: int
    is_active: bool
    tenant_id: UUID
'''

_WAREHOUSE = '''
"""Warehouse schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase, TimestampSchema


class WarehouseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=2, max_length=32, pattern=r"^[A-Z0-9\-]+$")
    address: str | None = None
    city: str | None = None
    country: str | None = None


class WarehouseUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    is_active: bool | None = None


class WarehouseResponse(ORMBase, TimestampSchema):
    id: UUID
    name: str
    code: str
    address: str | None
    city: str | None
    country: str | None
    is_active: bool
    tenant_id: UUID
'''

_INVENTORY = '''
"""Inventory and stock schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import ReservationStatus, StockAdjustmentType
from app.schemas.common import ORMBase, TimestampSchema


class InventoryItemResponse(ORMBase, TimestampSchema):
    id: UUID
    product_id: UUID
    warehouse_id: UUID
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    tenant_id: UUID


class StockAdjustmentCreate(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    adjustment_type: StockAdjustmentType
    quantity_delta: int = Field(..., description="Positive to add, negative to remove")
    reason: str | None = None
    reference: str | None = None


class StockAdjustmentResponse(ORMBase, TimestampSchema):
    id: UUID
    inventory_item_id: UUID
    adjustment_type: StockAdjustmentType
    quantity_delta: int
    quantity_before: int
    quantity_after: int
    reason: str | None
    reference: str | None


class StockReservationResponse(ORMBase, TimestampSchema):
    id: UUID
    order_id: UUID
    inventory_item_id: UUID
    quantity: int
    status: ReservationStatus
    expires_at: datetime | None
    reservation_ref: str
'''

_ORDER = '''
"""Order processing schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import OrderStatus
from app.schemas.common import ORMBase, TimestampSchema


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., ge=1)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: EmailStr | None = None
    warehouse_id: UUID
    items: list[OrderItemCreate] = Field(..., min_length=1)
    notes: str | None = None


class OrderItemResponse(ORMBase, TimestampSchema):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderResponse(ORMBase, TimestampSchema):
    id: UUID
    order_number: str
    status: OrderStatus
    customer_name: str
    customer_email: str | None
    warehouse_id: UUID
    subtotal: Decimal
    notes: str | None
    items: list[OrderItemResponse]
    tenant_id: UUID


class OrderCancelRequest(BaseModel):
    reason: str | None = None
'''

_TRANSFER = '''
"""Stock transfer schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import TransferStatus
from app.schemas.common import ORMBase, TimestampSchema


class TransferLineCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., ge=1)


class TransferCreate(BaseModel):
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    lines: list[TransferLineCreate] = Field(..., min_length=1)
    notes: str | None = None


class TransferLineResponse(ORMBase, TimestampSchema):
    id: UUID
    product_id: UUID
    quantity: int


class TransferResponse(ORMBase, TimestampSchema):
    id: UUID
    transfer_number: str
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    status: TransferStatus
    notes: str | None
    lines: list[TransferLineResponse]
    tenant_id: UUID
'''

_REPORT = '''
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
'''

_AUDIT = '''
"""Audit log schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import AuditAction, AuditEntityType
from app.schemas.common import ORMBase


class AuditLogResponse(ORMBase):
    id: UUID
    entity_type: AuditEntityType
    entity_id: UUID
    action: AuditAction
    actor_id: UUID | None
    actor_email: str | None
    description: str
    changes: dict | None
    ip_address: str | None
    correlation_id: str | None
    created_at: datetime
    tenant_id: UUID


class AuditLogFilter(BaseModel):
    entity_type: AuditEntityType | None = None
    entity_id: UUID | None = None
    action: AuditAction | None = None
    actor_id: UUID | None = None
'''
