"""Generate repository layer."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "app/repositories/__init__.py": '"""Data access repository layer."""\n',
        "app/repositories/base.py": _BASE,
        "app/repositories/tenant_repository.py": _TENANT,
        "app/repositories/user_repository.py": _USER,
        "app/repositories/product_repository.py": _PRODUCT,
        "app/repositories/warehouse_repository.py": _WAREHOUSE,
        "app/repositories/inventory_repository.py": _INVENTORY,
        "app/repositories/order_repository.py": _ORDER,
        "app/repositories/transfer_repository.py": _TRANSFER,
        "app/repositories/audit_repository.py": _AUDIT,
        "app/repositories/report_repository.py": _REPORT,
    }


_BASE = '''
"""Base repository with common CRUD operations."""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, stmt: Select | None = None) -> int:
        if stmt is None:
            stmt = select(func.count()).select_from(self.model)
        else:
            stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()
'''

_TENANT = '''
"""Tenant repository."""

from __future__ import annotations

from sqlalchemy import select

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    model = Tenant

    async def get_by_slug(self, slug: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, name: str, slug: str) -> Tenant:
        tenant = Tenant(name=name, slug=slug, is_active=True)
        self.session.add(tenant)
        await self.session.flush()
        return tenant
'''

_USER = '''
"""User repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.core.enums import UserRole
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, tenant_id: UUID, email: str) -> User | None:
        stmt = select(User).where(User.tenant_id == tenant_id, User.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: UUID, *, limit: int = 50, offset: int = 0
    ) -> list[User]:
        stmt = (
            select(User)
            .where(User.tenant_id == tenant_id)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        stmt = select(User).where(User.tenant_id == tenant_id)
        return await self.count(stmt)

    async def create(
        self,
        *,
        tenant_id: UUID,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole,
    ) -> User:
        user = User(
            tenant_id=tenant_id,
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()
        return user
'''

_PRODUCT = '''
"""Product repository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_, select

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def get_by_sku(self, tenant_id: UUID, sku: str) -> Product | None:
        stmt = select(Product).where(Product.tenant_id == tenant_id, Product.sku == sku)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        search: str | None = None,
        category: str | None = None,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        stmt = select(Product).where(Product.tenant_id == tenant_id)
        if active_only:
            stmt = stmt.where(Product.is_active.is_(True))
        if category:
            stmt = stmt.where(Product.category == category)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
        stmt = stmt.order_by(Product.name).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID, *, search: str | None = None) -> int:
        stmt = select(Product).where(Product.tenant_id == tenant_id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
        return await self.count(stmt)

    async def create(
        self,
        *,
        tenant_id: UUID,
        sku: str,
        name: str,
        category: str | None = None,
        unit_price: Decimal = Decimal("0"),
        reorder_point: int = 0,
        description: str | None = None,
    ) -> Product:
        product = Product(
            tenant_id=tenant_id,
            sku=sku,
            name=name,
            category=category,
            unit_price=unit_price,
            reorder_point=reorder_point,
            description=description,
            is_active=True,
        )
        self.session.add(product)
        await self.session.flush()
        return product
'''

_WAREHOUSE = '''
"""Warehouse repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.warehouse import Warehouse
from app.repositories.base import BaseRepository


class WarehouseRepository(BaseRepository[Warehouse]):
    model = Warehouse

    async def get_by_code(self, tenant_id: UUID, code: str) -> Warehouse | None:
        stmt = select(Warehouse).where(
            Warehouse.tenant_id == tenant_id, Warehouse.code == code.upper()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: UUID, *, active_only: bool = True, limit: int = 50, offset: int = 0
    ) -> list[Warehouse]:
        stmt = select(Warehouse).where(Warehouse.tenant_id == tenant_id)
        if active_only:
            stmt = stmt.where(Warehouse.is_active.is_(True))
        stmt = stmt.order_by(Warehouse.name).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        stmt = select(Warehouse).where(Warehouse.tenant_id == tenant_id)
        return await self.count(stmt)

    async def create(
        self,
        *,
        tenant_id: UUID,
        name: str,
        code: str,
        address: str | None = None,
        city: str | None = None,
        country: str | None = None,
    ) -> Warehouse:
        warehouse = Warehouse(
            tenant_id=tenant_id,
            name=name,
            code=code.upper(),
            address=address,
            city=city,
            country=country,
            is_active=True,
        )
        self.session.add(warehouse)
        await self.session.flush()
        return warehouse
'''

_INVENTORY = '''
"""Inventory repository with stock operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.enums import ReservationStatus, StockAdjustmentType
from app.models.inventory import InventoryItem
from app.models.stock_adjustment import StockAdjustment
from app.models.stock_reservation import StockReservation
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryItem]):
    model = InventoryItem

    async def get_or_create(
        self, tenant_id: UUID, product_id: UUID, warehouse_id: UUID
    ) -> InventoryItem:
        stmt = select(InventoryItem).where(
            InventoryItem.tenant_id == tenant_id,
            InventoryItem.product_id == product_id,
            InventoryItem.warehouse_id == warehouse_id,
        )
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        if item:
            return item
        item = InventoryItem(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity_on_hand=0,
            quantity_reserved=0,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def list_by_warehouse(
        self, tenant_id: UUID, warehouse_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> list[InventoryItem]:
        stmt = (
            select(InventoryItem)
            .options(selectinload(InventoryItem.product))
            .where(
                InventoryItem.tenant_id == tenant_id,
                InventoryItem.warehouse_id == warehouse_id,
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_tenant(
        self, tenant_id: UUID, *, warehouse_id: UUID | None = None, limit: int = 200, offset: int = 0
    ) -> list[InventoryItem]:
        stmt = select(InventoryItem).where(InventoryItem.tenant_id == tenant_id)
        if warehouse_id:
            stmt = stmt.where(InventoryItem.warehouse_id == warehouse_id)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def adjust_stock(
        self,
        *,
        item: InventoryItem,
        delta: int,
        adjustment_type: StockAdjustmentType,
        performed_by_id: UUID | None,
        reason: str | None = None,
        reference: str | None = None,
    ) -> StockAdjustment:
        before = item.quantity_on_hand
        after = before + delta
        if after < 0:
            raise ValueError("Stock cannot go negative")
        item.quantity_on_hand = after
        adjustment = StockAdjustment(
            tenant_id=item.tenant_id,
            inventory_item_id=item.id,
            adjustment_type=adjustment_type,
            quantity_delta=delta,
            quantity_before=before,
            quantity_after=after,
            reason=reason,
            reference=reference,
            performed_by_id=performed_by_id,
        )
        self.session.add(adjustment)
        await self.session.flush()
        return adjustment

    async def reserve_stock(
        self,
        *,
        item: InventoryItem,
        quantity: int,
        order_id: UUID,
        reservation_ref: str,
        expires_at,
    ) -> StockReservation:
        if item.quantity_available < quantity:
            raise ValueError("Insufficient available stock")
        item.quantity_reserved += quantity
        reservation = StockReservation(
            tenant_id=item.tenant_id,
            order_id=order_id,
            inventory_item_id=item.id,
            quantity=quantity,
            status=ReservationStatus.ACTIVE,
            reservation_ref=reservation_ref,
            expires_at=expires_at,
        )
        self.session.add(reservation)
        await self.session.flush()
        return reservation

    async def release_reservation(self, reservation: StockReservation) -> None:
        item = await self.get_by_id(reservation.inventory_item_id)
        if item:
            item.quantity_reserved = max(0, item.quantity_reserved - reservation.quantity)
        reservation.status = ReservationStatus.RELEASED
        await self.session.flush()

    async def consume_reservation(self, reservation: StockReservation) -> None:
        item = await self.get_by_id(reservation.inventory_item_id)
        if item:
            item.quantity_reserved = max(0, item.quantity_reserved - reservation.quantity)
            item.quantity_on_hand = max(0, item.quantity_on_hand - reservation.quantity)
        reservation.status = ReservationStatus.CONSUMED
        await self.session.flush()

    async def get_active_reservations(self, order_id: UUID) -> list[StockReservation]:
        stmt = select(StockReservation).where(
            StockReservation.order_id == order_id,
            StockReservation.status == ReservationStatus.ACTIVE,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
'''

_ORDER = '''
"""Order repository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.enums import OrderStatus
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order

    async def get_with_items(self, order_id: UUID) -> Order | None:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        status: OrderStatus | None = None,
        warehouse_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.tenant_id == tenant_id)
        )
        if status:
            stmt = stmt.where(Order.status == status)
        if warehouse_id:
            stmt = stmt.where(Order.warehouse_id == warehouse_id)
        stmt = stmt.order_by(Order.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID, *, status: OrderStatus | None = None) -> int:
        stmt = select(Order).where(Order.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Order.status == status)
        return await self.count(stmt)

    async def create_order(
        self,
        *,
        tenant_id: UUID,
        order_number: str,
        customer_name: str,
        warehouse_id: UUID,
        created_by_id: UUID | None,
        customer_email: str | None = None,
        notes: str | None = None,
        items: list[tuple[UUID, int, Decimal]],
    ) -> Order:
        subtotal = sum(price * qty for _, qty, price in items)
        order = Order(
            tenant_id=tenant_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            customer_name=customer_name,
            customer_email=customer_email,
            warehouse_id=warehouse_id,
            subtotal=subtotal,
            notes=notes,
            created_by_id=created_by_id,
        )
        self.session.add(order)
        await self.session.flush()

        for product_id, qty, price in items:
            line = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=qty,
                unit_price=price,
                line_total=price * qty,
            )
            self.session.add(line)
        await self.session.flush()
        await self.session.refresh(order, ["items"])
        return order

    async def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        await self.session.flush()
        return order
'''

_TRANSFER = '''
"""Stock transfer repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.enums import TransferStatus
from app.models.stock_transfer import StockTransfer, StockTransferLine
from app.repositories.base import BaseRepository


class TransferRepository(BaseRepository[StockTransfer]):
    model = StockTransfer

    async def get_with_lines(self, transfer_id: UUID) -> StockTransfer | None:
        stmt = (
            select(StockTransfer)
            .options(selectinload(StockTransfer.lines))
            .where(StockTransfer.id == transfer_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: UUID, *, limit: int = 50, offset: int = 0
    ) -> list[StockTransfer]:
        stmt = (
            select(StockTransfer)
            .options(selectinload(StockTransfer.lines))
            .where(StockTransfer.tenant_id == tenant_id)
            .order_by(StockTransfer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_transfer(
        self,
        *,
        tenant_id: UUID,
        transfer_number: str,
        source_warehouse_id: UUID,
        destination_warehouse_id: UUID,
        created_by_id: UUID | None,
        lines: list[tuple[UUID, int]],
        notes: str | None = None,
    ) -> StockTransfer:
        transfer = StockTransfer(
            tenant_id=tenant_id,
            transfer_number=transfer_number,
            source_warehouse_id=source_warehouse_id,
            destination_warehouse_id=destination_warehouse_id,
            status=TransferStatus.PENDING,
            notes=notes,
            created_by_id=created_by_id,
        )
        self.session.add(transfer)
        await self.session.flush()
        for product_id, qty in lines:
            line = StockTransferLine(transfer_id=transfer.id, product_id=product_id, quantity=qty)
            self.session.add(line)
        await self.session.flush()
        await self.session.refresh(transfer, ["lines"])
        return transfer
'''

_AUDIT = '''
"""Audit log repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.core.enums import AuditAction, AuditEntityType
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    model = AuditLog

    async def create_log(
        self,
        *,
        tenant_id: UUID,
        entity_type: AuditEntityType,
        entity_id: UUID,
        action: AuditAction,
        description: str,
        actor_id: UUID | None = None,
        actor_email: str | None = None,
        changes: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        correlation_id: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            actor_id=actor_id,
            actor_email=actor_email,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        entity_type: AuditEntityType | None = None,
        entity_id: UUID | None = None,
        action: AuditAction | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditLog.entity_id == entity_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
'''

_REPORT = '''
"""Report job repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.report_job import ReportJob, ReportJobStatus
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[ReportJob]):
    model = ReportJob

    async def create_job(
        self,
        *,
        tenant_id: UUID,
        report_type: str,
        parameters: dict | None,
        requested_by_id: UUID | None,
    ) -> ReportJob:
        job = ReportJob(
            tenant_id=tenant_id,
            report_type=report_type,
            status=ReportJobStatus.PENDING,
            parameters=parameters,
            requested_by_id=requested_by_id,
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_by_id_for_tenant(self, tenant_id: UUID, job_id: UUID) -> ReportJob | None:
        stmt = select(ReportJob).where(
            ReportJob.tenant_id == tenant_id, ReportJob.id == job_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_job(
        self,
        job: ReportJob,
        *,
        status: str | None = None,
        result: dict | None = None,
        error_message: str | None = None,
        celery_task_id: str | None = None,
    ) -> ReportJob:
        if status:
            job.status = status
        if result is not None:
            job.result = result
        if error_message is not None:
            job.error_message = error_message
        if celery_task_id:
            job.celery_task_id = celery_task_id
        await self.session.flush()
        return job
'''
