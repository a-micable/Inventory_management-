"""Inventory background tasks."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def expire_stale_reservations():
    async def _execute():
        from sqlalchemy import select, update
        from app.core.enums import ReservationStatus
        from app.database import session_scope
        from app.models.stock_reservation import StockReservation
        from app.repositories.inventory_repository import InventoryRepository
        from app.utils.datetime_utils import utc_now

        async with session_scope() as db:
            now = utc_now()
            stmt = select(StockReservation).where(
                StockReservation.status == ReservationStatus.ACTIVE,
                StockReservation.expires_at < now,
            )
            result = await db.execute(stmt)
            reservations = list(result.scalars().all())
            repo = InventoryRepository(db)
            for reservation in reservations:
                await repo.release_reservation(reservation)
                reservation.status = ReservationStatus.EXPIRED
            logger.info("Expired %d stale reservations", len(reservations))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_execute())
    finally:
        loop.close()


@celery_app.task
def warm_inventory_cache():
    async def _execute():
        from sqlalchemy import select
        from app.core.cache import cache_set
        from app.core.constants import INVENTORY_CACHE_PREFIX
        from app.database import session_scope
        from app.models.tenant import Tenant

        async with session_scope() as db:
            result = await db.execute(select(Tenant).where(Tenant.is_active.is_(True)))
            tenants = list(result.scalars().all())
            for tenant in tenants:
                await cache_set(
                    f"{INVENTORY_CACHE_PREFIX}{tenant.id}:warm",
                    {"warmed_at": str(utc_now())},
                    ttl=1800,
                )
            logger.info("Warmed inventory cache for %d tenants", len(tenants))

    from app.utils.datetime_utils import utc_now
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_execute())
    finally:
        loop.close()
