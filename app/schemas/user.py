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
