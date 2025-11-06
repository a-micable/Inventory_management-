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
