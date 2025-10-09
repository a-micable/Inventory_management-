"""User management service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntityType, UserRole
from app.core.exceptions import ConflictError, NotFoundError
from app.core.permissions import require_permission
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.audit_service import AuditService
from app.utils.pagination import Page, PageParams
from app.utils.validators import validate_password


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)
        self.audit = AuditService(session)

    async def list_users(
        self, tenant_id: UUID, params: PageParams, *, actor_role: UserRole
    ) -> Page[UserResponse]:
        require_permission(actor_role, "users:read")
        items = await self.repo.list_by_tenant(
            tenant_id, limit=params.page_size, offset=params.offset
        )
        total = await self.repo.count_by_tenant(tenant_id)
        return Page(
            items=[UserResponse.model_validate(u) for u in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def create_user(
        self,
        tenant_id: UUID,
        data: UserCreate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> UserResponse:
        require_permission(actor_role, "users:write")
        validate_password(data.password)
        existing = await self.repo.get_by_email(tenant_id, data.email)
        if existing:
            raise ConflictError("Email already registered for this tenant")
        user = await self.repo.create(
            tenant_id=tenant_id,
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
        )
        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.CREATE,
            description=f"Created user {user.email} with role {user.role.value}",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        return UserResponse.model_validate(user)

    async def update_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        data: UserUpdate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> UserResponse:
        require_permission(actor_role, "users:write")
        user = await self.repo.get_by_id(user_id)
        if not user or user.tenant_id != tenant_id:
            raise NotFoundError("User not found")
        changes = {}
        if data.full_name is not None:
            changes["full_name"] = {"from": user.full_name, "to": data.full_name}
            user.full_name = data.full_name
        if data.role is not None:
            changes["role"] = {"from": user.role.value, "to": data.role.value}
            user.role = data.role
        if data.is_active is not None:
            changes["is_active"] = {"from": user.is_active, "to": data.is_active}
            user.is_active = data.is_active
        await self.session.flush()
        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.UPDATE,
            description=f"Updated user {user.email}",
            actor_id=actor_id,
            actor_email=actor_email,
            changes=changes or None,
        )
        return UserResponse.model_validate(user)

    @property
    def session(self) -> AsyncSession:
        return self.repo.session
