"""Generate API routers."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "app/routers/__init__.py": '"""API route modules."""\n',
        "app/routers/auth.py": _AUTH,
        "app/routers/users.py": _USERS,
        "app/routers/products.py": _PRODUCTS,
        "app/routers/warehouses.py": _WAREHOUSES,
        "app/routers/inventory.py": _INVENTORY,
        "app/routers/orders.py": _ORDERS,
        "app/routers/reports.py": _REPORTS,
        "app/routers/audit.py": _AUDIT,
    }


_AUTH = '''
"""Authentication endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.database import get_db
from app.dependencies.rate_limit import limiter
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenRefreshRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens, user = await service.register(data)
    return success_response({"tokens": tokens.model_dump(), "user": user.model_dump()})


@router.post("/login", response_model=dict)
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens, user = await service.login(data)
    return success_response({"tokens": tokens.model_dump(), "user": user.model_dump()})


@router.post("/refresh", response_model=dict)
async def refresh_token(data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens = await service.refresh(data.refresh_token)
    return success_response(tokens.model_dump())
'''

_USERS = '''
"""User management endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PageParams
from app.utils.response import success_response

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    result = await service.list_users(
        current_user.tenant_id, PageParams(page, page_size), actor_role=current_user.role
    )
    return success_response({
        "items": result.items,
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "total_pages": result.total_pages,
    })


@router.post("", response_model=dict)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.create_user(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(user.model_dump())


@router.patch("/{user_id}", response_model=dict)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.update_user(
        current_user.tenant_id,
        user_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(user.model_dump())
'''

_PRODUCTS = '''
"""Product catalog endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.utils.pagination import PageParams
from app.utils.response import success_response

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    result = await service.list_products(
        current_user.tenant_id,
        PageParams(page, page_size),
        search=search,
        category=category,
        actor_role=current_user.role,
    )
    return success_response({
        "items": [i.model_dump() for i in result.items],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
    })


@router.get("/{product_id}")
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    product = await service.get_product(
        current_user.tenant_id, product_id, actor_role=current_user.role
    )
    return success_response(product.model_dump())


@router.post("")
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    product = await service.create_product(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(product.model_dump())


@router.patch("/{product_id}")
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    product = await service.update_product(
        current_user.tenant_id,
        product_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(product.model_dump())
'''

_WAREHOUSES = '''
"""Warehouse endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.warehouse import WarehouseCreate
from app.services.warehouse_service import WarehouseService
from app.utils.pagination import PageParams
from app.utils.response import success_response

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("")
async def list_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    result = await service.list_warehouses(
        current_user.tenant_id, PageParams(page, page_size), actor_role=current_user.role
    )
    return success_response({
        "items": [i.model_dump() for i in result.items],
        "total": result.total,
    })


@router.get("/{warehouse_id}")
async def get_warehouse(
    warehouse_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    wh = await service.get_warehouse(
        current_user.tenant_id, warehouse_id, actor_role=current_user.role
    )
    return success_response(wh.model_dump())


@router.post("")
async def create_warehouse(
    data: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    wh = await service.create_warehouse(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(wh.model_dump())
'''

_INVENTORY = '''
"""Inventory management endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.inventory import StockAdjustmentCreate
from app.schemas.transfer import TransferCreate
from app.services.inventory_service import InventoryService
from app.services.transfer_service import TransferService
from app.utils.pagination import PageParams
from app.utils.response import success_response

router = APIRouter(tags=["inventory"])


@router.get("/inventory")
async def list_inventory(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    warehouse_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InventoryService(db)
    result = await service.list_inventory(
        current_user.tenant_id,
        PageParams(page, page_size),
        warehouse_id=warehouse_id,
        actor_role=current_user.role,
    )
    return success_response({
        "items": [i.model_dump() for i in result.items],
        "total": result.total,
    })


@router.post("/inventory/adjustments")
async def adjust_stock(
    data: StockAdjustmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InventoryService(db)
    adjustment = await service.adjust_stock(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(adjustment.model_dump())


@router.get("/transfers")
async def list_transfers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TransferService(db)
    result = await service.list_transfers(
        current_user.tenant_id, PageParams(page, page_size), actor_role=current_user.role
    )
    return success_response({"items": [i.model_dump() for i in result.items]})


@router.post("/transfers")
async def create_transfer(
    data: TransferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TransferService(db)
    transfer = await service.create_transfer(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(transfer.model_dump())


@router.post("/transfers/{transfer_id}/complete")
async def complete_transfer(
    transfer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TransferService(db)
    transfer = await service.complete_transfer(
        current_user.tenant_id,
        transfer_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(transfer.model_dump())
'''

_ORDERS = '''
"""Order processing endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import OrderStatus
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.order import OrderCancelRequest, OrderCreate
from app.services.order_service import OrderService
from app.utils.pagination import PageParams
from app.utils.response import success_response

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: OrderStatus | None = None,
    warehouse_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)
    result = await service.list_orders(
        current_user.tenant_id,
        PageParams(page, page_size),
        status=status,
        warehouse_id=warehouse_id,
        actor_role=current_user.role,
    )
    return success_response({
        "items": [i.model_dump() for i in result.items],
        "total": result.total,
    })


@router.get("/{order_id}")
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)
    order = await service.get_order(
        current_user.tenant_id, order_id, actor_role=current_user.role
    )
    return success_response(order.model_dump())


@router.post("")
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)
    order = await service.create_order(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(order.model_dump())


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: UUID,
    data: OrderCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)
    order = await service.cancel_order(
        current_user.tenant_id,
        order_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(order.model_dump())


@router.post("/{order_id}/fulfill")
async def fulfill_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OrderService(db)
    order = await service.fulfill_order(
        current_user.tenant_id,
        order_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(order.model_dump())
'''

_REPORTS = '''
"""Report generation endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.report import InventoryReportRequest, SalesReportRequest
from app.services.report_service import ReportService
from app.utils.response import success_response

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/inventory")
async def inventory_report(
    data: InventoryReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReportService(db)
    report = await service.inventory_report(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(report.model_dump())


@router.post("/sales")
async def sales_report(
    data: SalesReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReportService(db)
    report = await service.sales_report(
        current_user.tenant_id,
        data,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )
    return success_response(report.model_dump())


@router.post("/async/{report_type}")
async def async_report(
    report_type: str,
    parameters: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReportService(db)
    job = await service.enqueue_report(
        current_user.tenant_id,
        report_type,
        parameters,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )
    return success_response(job.model_dump())
'''

_AUDIT = '''
"""Audit log endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntityType
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogResponse
from app.utils.response import success_response

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    entity_type: AuditEntityType | None = None,
    entity_id: UUID | None = None,
    action: AuditAction | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.core.permissions import require_permission
    require_permission(current_user.role, "audit:read")

    repo = AuditRepository(db)
    offset = (page - 1) * page_size
    logs = await repo.list_by_tenant(
        current_user.tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        limit=page_size,
        offset=offset,
    )
    return success_response({
        "items": [AuditLogResponse.model_validate(log).model_dump() for log in logs],
        "page": page,
        "page_size": page_size,
    })
'''
