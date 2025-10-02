"""Inter-warehouse stock transfer service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntityType, StockAdjustmentType, TransferStatus, UserRole
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.permissions import require_permission
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.transfer_repository import TransferRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.transfer import TransferCreate, TransferResponse
from app.services.audit_service import AuditService
from app.services.number_generator import generate_transfer_number
from app.utils.pagination import Page, PageParams


class TransferService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TransferRepository(session)
        self.inventory_repo = InventoryRepository(session)
        self.product_repo = ProductRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.audit = AuditService(session)

    async def list_transfers(
        self, tenant_id: UUID, params: PageParams, *, actor_role: UserRole
    ) -> Page[TransferResponse]:
        require_permission(actor_role, "inventory:read")
        transfers = await self.repo.list_by_tenant(
            tenant_id, limit=params.page_size, offset=params.offset
        )
        return Page(
            items=[TransferResponse.model_validate(t) for t in transfers],
            total=len(transfers),
            page=params.page,
            page_size=params.page_size,
        )

    async def create_transfer(
        self,
        tenant_id: UUID,
        data: TransferCreate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> TransferResponse:
        require_permission(actor_role, "inventory:transfer")
        if data.source_warehouse_id == data.destination_warehouse_id:
            raise ValidationError("Source and destination warehouses must differ")

        source = await self.warehouse_repo.get_by_id(data.source_warehouse_id)
        dest = await self.warehouse_repo.get_by_id(data.destination_warehouse_id)
        if not source or source.tenant_id != tenant_id:
            raise NotFoundError("Source warehouse not found")
        if not dest or dest.tenant_id != tenant_id:
            raise NotFoundError("Destination warehouse not found")

        lines: list[tuple[UUID, int]] = []
        for line in data.lines:
            product = await self.product_repo.get_by_id(line.product_id)
            if not product or product.tenant_id != tenant_id:
                raise NotFoundError(f"Product {line.product_id} not found")
            source_item = await self.inventory_repo.get_or_create(
                tenant_id, line.product_id, data.source_warehouse_id
            )
            if source_item.quantity_available < line.quantity:
                raise ConflictError(
                    f"Insufficient stock for {product.sku} at {source.code}"
                )
            lines.append((line.product_id, line.quantity))

        transfer = await self.repo.create_transfer(
            tenant_id=tenant_id,
            transfer_number=generate_transfer_number(),
            source_warehouse_id=data.source_warehouse_id,
            destination_warehouse_id=data.destination_warehouse_id,
            created_by_id=actor_id,
            lines=lines,
            notes=data.notes,
        )

        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.TRANSFER,
            entity_id=transfer.id,
            action=AuditAction.CREATE,
            description=f"Created transfer {transfer.transfer_number}",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        return TransferResponse.model_validate(transfer)

    async def complete_transfer(
        self,
        tenant_id: UUID,
        transfer_id: UUID,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> TransferResponse:
        require_permission(actor_role, "inventory:transfer")
        transfer = await self.repo.get_with_lines(transfer_id)
        if not transfer or transfer.tenant_id != tenant_id:
            raise NotFoundError("Transfer not found")
        if transfer.status != TransferStatus.PENDING:
            raise ConflictError(f"Transfer is {transfer.status.value}, cannot complete")

        for line in transfer.lines:
            source_item = await self.inventory_repo.get_or_create(
                tenant_id, line.product_id, transfer.source_warehouse_id
            )
            dest_item = await self.inventory_repo.get_or_create(
                tenant_id, line.product_id, transfer.destination_warehouse_id
            )
            await self.inventory_repo.adjust_stock(
                item=source_item,
                delta=-line.quantity,
                adjustment_type=StockAdjustmentType.CORRECTION,
                performed_by_id=actor_id,
                reason=f"Transfer out {transfer.transfer_number}",
            )
            await self.inventory_repo.adjust_stock(
                item=dest_item,
                delta=line.quantity,
                adjustment_type=StockAdjustmentType.RECEIPT,
                performed_by_id=actor_id,
                reason=f"Transfer in {transfer.transfer_number}",
            )

        transfer.status = TransferStatus.COMPLETED
        await self.repo.session.flush()

        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.TRANSFER,
            entity_id=transfer.id,
            action=AuditAction.TRANSFER,
            description=f"Completed transfer {transfer.transfer_number}",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        return TransferResponse.model_validate(transfer)
