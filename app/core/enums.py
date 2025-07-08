"""Domain enumerations used across the platform."""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class StockAdjustmentType(str, enum.Enum):
    RECEIPT = "receipt"
    DAMAGE = "damage"
    CORRECTION = "correction"
    RETURN = "return"
    CYCLE_COUNT = "cycle_count"


class ReservationStatus(str, enum.Enum):
    ACTIVE = "active"
    RELEASED = "released"
    CONSUMED = "consumed"
    EXPIRED = "expired"


class TransferStatus(str, enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ADJUST = "adjust"
    RESERVE = "reserve"
    RELEASE = "release"
    TRANSFER = "transfer"
    FULFILL = "fulfill"
    CANCEL = "cancel"
    LOGIN = "login"
    REGISTER = "register"


class AuditEntityType(str, enum.Enum):
    USER = "user"
    PRODUCT = "product"
    INVENTORY = "inventory"
    ORDER = "order"
    WAREHOUSE = "warehouse"
    TRANSFER = "transfer"
    RESERVATION = "reservation"
    REPORT = "report"
