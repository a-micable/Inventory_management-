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
