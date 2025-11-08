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
