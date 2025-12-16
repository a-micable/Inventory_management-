"""Service layer dependency factories."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.report_service import ReportService
from app.services.transfer_service import TransferService
from app.services.user_service import UserService
from app.services.warehouse_service import WarehouseService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


def get_warehouse_service(db: AsyncSession = Depends(get_db)) -> WarehouseService:
    return WarehouseService(db)


def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(db)


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)


def get_transfer_service(db: AsyncSession = Depends(get_db)) -> TransferService:
    return TransferService(db)


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)
