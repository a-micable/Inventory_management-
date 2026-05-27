"""Business policy rules enforced at the domain layer."""

from __future__ import annotations

from app.core.enums import OrderStatus, TransferStatus, UserRole
from app.core.exceptions import AuthorizationError, ConflictError, ValidationError


class OrderPolicy:
    FULFILLABLE_STATUSES = {OrderStatus.CONFIRMED}
    CANCELLABLE_STATUSES = {OrderStatus.DRAFT, OrderStatus.PENDING, OrderStatus.CONFIRMED}

    @staticmethod
    def can_fulfill(status: OrderStatus) -> None:
        if status not in OrderPolicy.FULFILLABLE_STATUSES:
            raise ValidationError(f"Order in status '{status.value}' cannot be fulfilled")

    @staticmethod
    def can_cancel(status: OrderStatus) -> None:
        if status not in OrderPolicy.CANCELLABLE_STATUSES:
            raise ConflictError(f"Order in status '{status.value}' cannot be cancelled")


class TransferPolicy:
    @staticmethod
    def can_complete(status: TransferStatus) -> None:
        if status != TransferStatus.PENDING:
            raise ConflictError(f"Transfer in status '{status.value}' cannot be completed")

    @staticmethod
    def validate_warehouses(source_id, dest_id) -> None:
        if source_id == dest_id:
            raise ValidationError("Source and destination warehouses must be different")


class StockPolicy:
    @staticmethod
    def validate_adjustment(current: int, delta: int) -> int:
        result = current + delta
        if result < 0:
            raise ValidationError(f"Adjustment would result in negative stock: {result}")
        return result

    @staticmethod
    def validate_reservation(available: int, requested: int) -> None:
        if available < requested:
            raise ValidationError(
                f"Insufficient stock: available={available}, requested={requested}"
            )


class RolePolicy:
    @staticmethod
    def can_manage_users(role: UserRole) -> None:
        if role != UserRole.ADMIN:
            raise AuthorizationError("Only admins can manage users")

    @staticmethod
    def can_view_audit(role: UserRole) -> None:
        if role != UserRole.ADMIN:
            raise AuthorizationError("Only admins can view audit logs")
