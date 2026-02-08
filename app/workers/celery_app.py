"""Celery application configuration."""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "inventory_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.report_tasks",
        "app.workers.inventory_tasks",
        "app.workers.maintenance_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "expire-stale-reservations": {
            "task": "app.workers.inventory_tasks.expire_stale_reservations",
            "schedule": 3600.0,
        },
        "warm-inventory-cache": {
            "task": "app.workers.inventory_tasks.warm_inventory_cache",
            "schedule": 1800.0,
        },
        "purge-old-audit-logs": {
            "task": "app.workers.maintenance_tasks.purge_old_audit_logs",
            "schedule": 86400.0,
        },
    },
)
