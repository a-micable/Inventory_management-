"""Product catalog service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_delete, cache_set
from app.core.constants import PRODUCT_CACHE_PREFIX
from app.core.enums import AuditAction, AuditEntityType, UserRole
from app.core.exceptions import ConflictError, NotFoundError
from app.core.permissions import require_permission
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.audit_service import AuditService
from app.utils.pagination import Page, PageParams
from app.utils.validators import validate_sku


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ProductRepository(session)
        self.audit = AuditService(session)

    async def list_products(
        self,
        tenant_id: UUID,
        params: PageParams,
        *,
        search: str | None = None,
        category: str | None = None,
        actor_role: UserRole,
    ) -> Page[ProductResponse]:
        require_permission(actor_role, "products:read")
        items = await self.repo.list_by_tenant(
            tenant_id,
            search=search,
            category=category,
            limit=params.page_size,
            offset=params.offset,
        )
        total = await self.repo.count_by_tenant(tenant_id, search=search)
        return Page(
            items=[ProductResponse.model_validate(p) for p in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_product(
        self, tenant_id: UUID, product_id: UUID, *, actor_role: UserRole
    ) -> ProductResponse:
        require_permission(actor_role, "products:read")
        product = await self.repo.get_by_id(product_id)
        if not product or product.tenant_id != tenant_id:
            raise NotFoundError("Product not found")
        return ProductResponse.model_validate(product)

    async def create_product(
        self,
        tenant_id: UUID,
        data: ProductCreate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> ProductResponse:
        require_permission(actor_role, "products:write")
        sku = validate_sku(data.sku)
        if await self.repo.get_by_sku(tenant_id, sku):
            raise ConflictError(f"SKU '{sku}' already exists")
        product = await self.repo.create(
            tenant_id=tenant_id,
            sku=sku,
            name=data.name,
            description=data.description,
            category=data.category,
            unit_price=data.unit_price,
            reorder_point=data.reorder_point,
        )
        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.PRODUCT,
            entity_id=product.id,
            action=AuditAction.CREATE,
            description=f"Created product {product.sku}: {product.name}",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        await cache_delete(f"{PRODUCT_CACHE_PREFIX}{tenant_id}:*")
        return ProductResponse.model_validate(product)

    async def update_product(
        self,
        tenant_id: UUID,
        product_id: UUID,
        data: ProductUpdate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> ProductResponse:
        require_permission(actor_role, "products:write")
        product = await self.repo.get_by_id(product_id)
        if not product or product.tenant_id != tenant_id:
            raise NotFoundError("Product not found")
        changes = {}
        for field in ("name", "description", "category", "unit_price", "reorder_point", "is_active"):
            value = getattr(data, field)
            if value is not None:
                changes[field] = {"from": str(getattr(product, field)), "to": str(value)}
                setattr(product, field, value)
        await self.repo.session.flush()
        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.PRODUCT,
            entity_id=product.id,
            action=AuditAction.UPDATE,
            description=f"Updated product {product.sku}",
            actor_id=actor_id,
            actor_email=actor_email,
            changes=changes or None,
        )
        await cache_set(f"{PRODUCT_CACHE_PREFIX}{tenant_id}:{product_id}", ProductResponse.model_validate(product).model_dump())
        return ProductResponse.model_validate(product)
