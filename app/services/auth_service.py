"""Authentication and registration service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.enums import AuditAction, AuditEntityType, UserRole
from app.core.exceptions import AuthenticationError, ConflictError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthUserResponse, LoginRequest, RegisterRequest, TokenResponse
from app.services.audit_service import AuditService
from app.utils.validators import validate_password

settings = get_settings()


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tenant_repo = TenantRepository(session)
        self.user_repo = UserRepository(session)
        self.audit = AuditService(session)

    async def register(self, data: RegisterRequest) -> tuple[TokenResponse, AuthUserResponse]:
        validate_password(data.password)
        existing_tenant = await self.tenant_repo.get_by_slug(data.tenant_slug)
        if existing_tenant:
            raise ConflictError(f"Tenant slug '{data.tenant_slug}' already exists")

        tenant = await self.tenant_repo.create(name=data.tenant_name, slug=data.tenant_slug)
        user = await self.user_repo.create(
            tenant_id=tenant.id,
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=UserRole.ADMIN,
        )

        await self.audit.log(
            tenant_id=tenant.id,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.REGISTER,
            description=f"User {user.email} registered new tenant {tenant.slug}",
            actor_id=user.id,
            actor_email=user.email,
        )

        tokens = self._build_tokens(user.id, tenant.id, user.role)
        return tokens, AuthUserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> tuple[TokenResponse, AuthUserResponse]:
        tenant = await self.tenant_repo.get_by_slug(data.tenant_slug)
        if not tenant or not tenant.is_active:
            raise AuthenticationError("Invalid tenant or credentials")

        user = await self.user_repo.get_by_email(tenant.id, data.email)
        if not user or not user.is_active:
            raise AuthenticationError("Invalid tenant or credentials")
        if not verify_password(data.password, user.hashed_password):
            raise AuthenticationError("Invalid tenant or credentials")

        await self.audit.log(
            tenant_id=tenant.id,
            entity_type=AuditEntityType.USER,
            entity_id=user.id,
            action=AuditAction.LOGIN,
            description=f"User {user.email} logged in",
            actor_id=user.id,
            actor_email=user.email,
        )

        tokens = self._build_tokens(user.id, tenant.id, user.role)
        return tokens, AuthUserResponse.model_validate(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        user_id = UUID(payload["sub"])
        tenant_id = UUID(payload["tenant_id"])
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.tenant_id != tenant_id or not user.is_active:
            raise AuthenticationError("User no longer valid")
        return self._build_tokens(user.id, tenant_id, user.role)

    def _build_tokens(self, user_id: UUID, tenant_id: UUID, role: UserRole) -> TokenResponse:
        access = create_access_token(subject=str(user_id), tenant_id=tenant_id, role=role.value)
        refresh = create_refresh_token(subject=str(user_id), tenant_id=tenant_id)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.access_token_expire_minutes * 60,
        )
