"""Warehouse management service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntityType, UserRole
from app.core.exceptions import ConflictError, NotFoundError
from app.core.permissions import require_permission
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.warehouse import WarehouseCreate, WarehouseResponse, WarehouseUpdate
from app.services.audit_service import AuditService
from app.utils.pagination import Page, PageParams


class WarehouseService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = WarehouseRepository(session)
        self.audit = AuditService(session)

    async def list_warehouses(
        self, tenant_id: UUID, params: PageParams, *, actor_role: UserRole
    ) -> Page[WarehouseResponse]:
        require_permission(actor_role, "warehouses:read")
        items = await self.repo.list_by_tenant(
            tenant_id, limit=params.page_size, offset=params.offset
        )
        total = await self.repo.count_by_tenant(tenant_id)
        return Page(
            items=[WarehouseResponse.model_validate(w) for w in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def create_warehouse(
        self,
        tenant_id: UUID,
        data: WarehouseCreate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> WarehouseResponse:
        require_permission(actor_role, "warehouses:write")
        if await self.repo.get_by_code(tenant_id, data.code):
            raise ConflictError(f"Warehouse code '{data.code}' already exists")
        warehouse = await self.repo.create(
            tenant_id=tenant_id,
            name=data.name,
            code=data.code,
            address=data.address,
            city=data.city,
            country=data.country,
        )
        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.WAREHOUSE,
            entity_id=warehouse.id,
            action=AuditAction.CREATE,
            description=f"Created warehouse {warehouse.code}: {warehouse.name}",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        return WarehouseResponse.model_validate(warehouse)

    async def get_warehouse(
        self, tenant_id: UUID, warehouse_id: UUID, *, actor_role: UserRole
    ) -> WarehouseResponse:
        require_permission(actor_role, "warehouses:read")
        warehouse = await self.repo.get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise NotFoundError("Warehouse not found")
        return WarehouseResponse.model_validate(warehouse)
