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
