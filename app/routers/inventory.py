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
