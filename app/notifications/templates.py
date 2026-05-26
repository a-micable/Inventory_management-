"""Notification message templates."""

from __future__ import annotations


def low_stock_template(sku: str, warehouse: str, quantity: int, reorder_point: int) -> str:
    return (
        f"ALERT: Stock level for {sku} at {warehouse} is {quantity} "
        f"(reorder point: {reorder_point}). Please replenish inventory."
    )


def order_fulfilled_template(order_number: str, customer_name: str) -> str:
    return f"Order {order_number} for {customer_name} has been fulfilled and shipped."


def transfer_completed_template(transfer_number: str, source: str, dest: str) -> str:
    return (
        f"Stock transfer {transfer_number} from {source} to {dest} "
        f"has been completed successfully."
    )


def welcome_template(tenant_name: str, admin_email: str) -> str:
    return (
        f"Welcome to the Inventory Platform! Your organization '{tenant_name}' "
        f"has been registered. Admin account: {admin_email}"
    )
