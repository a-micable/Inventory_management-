"""Order processing service with inventory integration."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntityType, OrderStatus, UserRole
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.permissions import require_permission
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.order import OrderCancelRequest, OrderCreate, OrderResponse
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService
from app.services.number_generator import generate_order_number
from app.utils.pagination import Page, PageParams


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OrderRepository(session)
        self.product_repo = ProductRepository(session)
        self.warehouse_repo = WarehouseRepository(session)
        self.inventory = InventoryService(session)
        self.audit = AuditService(session)

    async def list_orders(
        self,
        tenant_id: UUID,
        params: PageParams,
        *,
        status: OrderStatus | None = None,
        warehouse_id: UUID | None = None,
        actor_role: UserRole,
    ) -> Page[OrderResponse]:
        require_permission(actor_role, "orders:read")
        orders = await self.repo.list_by_tenant(
            tenant_id,
            status=status,
            warehouse_id=warehouse_id,
            limit=params.page_size,
            offset=params.offset,
        )
        total = await self.repo.count_by_tenant(tenant_id, status=status)
        return Page(
            items=[OrderResponse.model_validate(o) for o in orders],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_order(
        self, tenant_id: UUID, order_id: UUID, *, actor_role: UserRole
    ) -> OrderResponse:
        require_permission(actor_role, "orders:read")
        order = await self.repo.get_with_items(order_id)
        if not order or order.tenant_id != tenant_id:
            raise NotFoundError("Order not found")
        return OrderResponse.model_validate(order)

    async def create_order(
        self,
        tenant_id: UUID,
        data: OrderCreate,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> OrderResponse:
        require_permission(actor_role, "orders:create")
        warehouse = await self.warehouse_repo.get_by_id(data.warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise NotFoundError("Warehouse not found")

        line_data: list[tuple] = []
        for item in data.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if not product or product.tenant_id != tenant_id or not product.is_active:
                raise NotFoundError(f"Product {item.product_id} not found")
            line_data.append((product.id, item.quantity, product.unit_price))

        order = await self.repo.create_order(
            tenant_id=tenant_id,
            order_number=generate_order_number(),
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            warehouse_id=data.warehouse_id,
            created_by_id=actor_id,
            notes=data.notes,
            items=line_data,
        )

        for product_id, qty, _ in line_data:
            await self.inventory.reserve_for_order(
                tenant_id,
                order.id,
                product_id,
                data.warehouse_id,
                qty,
                actor_id=actor_id,
                actor_email=actor_email,
            )

        await self.repo.update_status(order, OrderStatus.CONFIRMED)

        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.ORDER,
            entity_id=order.id,
            action=AuditAction.CREATE,
            description=f"Created order {order.order_number} for {order.customer_name}",
            actor_id=actor_id,
            actor_email=actor_email,
            changes={"items": len(data.items), "subtotal": str(order.subtotal)},
        )
        order = await self.repo.get_with_items(order.id)
        return OrderResponse.model_validate(order)

    async def cancel_order(
        self,
        tenant_id: UUID,
        order_id: UUID,
        data: OrderCancelRequest,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> OrderResponse:
        require_permission(actor_role, "orders:cancel")
        order = await self.repo.get_with_items(order_id)
        if not order or order.tenant_id != tenant_id:
            raise NotFoundError("Order not found")
        if order.status in (OrderStatus.FULFILLED, OrderStatus.CANCELLED):
            raise ConflictError(f"Cannot cancel order in status {order.status.value}")

        await self.inventory.release_order_reservations(
            tenant_id, order.id, actor_id=actor_id, actor_email=actor_email
        )
        await self.repo.update_status(order, OrderStatus.CANCELLED)

        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.ORDER,
            entity_id=order.id,
            action=AuditAction.CANCEL,
            description=f"Cancelled order {order.order_number}",
            actor_id=actor_id,
            actor_email=actor_email,
            changes={"reason": data.reason},
        )
        return OrderResponse.model_validate(order)

    async def fulfill_order(
        self,
        tenant_id: UUID,
        order_id: UUID,
        *,
        actor_id: UUID,
        actor_email: str,
        actor_role: UserRole,
    ) -> OrderResponse:
        require_permission(actor_role, "orders:fulfill")
        order = await self.repo.get_with_items(order_id)
        if not order or order.tenant_id != tenant_id:
            raise NotFoundError("Order not found")
        if order.status != OrderStatus.CONFIRMED:
            raise ValidationError(f"Order must be confirmed to fulfill, current: {order.status.value}")

        reservations = await self.inventory.repo.get_active_reservations(order.id)
        for reservation in reservations:
            await self.inventory.repo.consume_reservation(reservation)
            await self.audit.log(
                tenant_id=tenant_id,
                entity_type=AuditEntityType.RESERVATION,
                entity_id=reservation.id,
                action=AuditAction.FULFILL,
                description=f"Consumed reservation for order {order.order_number}",
                actor_id=actor_id,
                actor_email=actor_email,
            )

        order.fulfilled_by_id = actor_id
        await self.repo.update_status(order, OrderStatus.FULFILLED)

        await self.audit.log(
            tenant_id=tenant_id,
            entity_type=AuditEntityType.ORDER,
            entity_id=order.id,
            action=AuditAction.FULFILL,
            description=f"Fulfilled order {order.order_number}",
            actor_id=actor_id,
            actor_email=actor_email,
        )
        return OrderResponse.model_validate(order)
