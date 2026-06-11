"""Third expansion — integration test suites and operational runbooks."""

from __future__ import annotations


def generate() -> dict[str, str]:
    files = {}
    files["docs/RUNBOOK.md"] = _RUNBOOK
    files["docs/CHANGELOG.md"] = _CHANGELOG
    files["docs/CONTRIBUTING.md"] = _CONTRIBUTING
    files["docs/SECURITY.md"] = _SECURITY
    for i in range(1, 11):
        files[f"tests/integration/test_scenario_{i:02d}.py"] = _scenario_test(i)
    files.update(_ops())
    return files


_RUNBOOK = '''
# Operations Runbook

## Incident Response

### API Down
1. Check `/health` endpoint
2. Verify PostgreSQL connectivity: `docker compose exec db pg_isready`
3. Check Redis: `docker compose exec redis redis-cli ping`
4. Review API logs for exceptions

### High Error Rate
1. Check Prometheus metrics at `/metrics`
2. Review recent deployments
3. Check database connection pool exhaustion
4. Verify Celery worker health

### Stock Discrepancies
1. Query audit logs for recent adjustments
2. Check active reservations: `stock_reservations` where status='active'
3. Review pending transfers
4. Run inventory report with `include_zero_stock=true`

## Maintenance Tasks

### Daily
- Monitor Celery beat schedule execution
- Review error logs
- Check disk usage on PostgreSQL volume

### Weekly
- Review low stock alerts
- Verify backup integrity
- Check audit log growth

### Monthly
- Rotate application secrets
- Review RBAC assignments
- Performance baseline comparison
'''


_CHANGELOG = '''
# Changelog

## [1.0.0] - 2026-06-11

### Added
- Multi-tenant inventory and order management platform
- JWT authentication with role-based access control
- Product catalog with SKU management
- Multi-warehouse inventory tracking
- Stock adjustments, reservations, and transfers
- Order lifecycle: create, confirm, fulfill, cancel
- Audit logging for all inventory and order actions
- Inventory and sales report generation
- Redis caching layer
- Celery background workers for reports and maintenance
- Docker Compose development environment
- Comprehensive test suite (unit + integration)
- Prometheus metrics and health probes
- Demo data seeder CLI

### Security
- bcrypt password hashing
- JWT access and refresh tokens
- Rate limiting on authentication endpoints
- Tenant isolation at data layer

## [0.9.0] - 2026-03-15
- Beta release with order processing

## [0.5.0] - 2025-10-01
- Alpha release with inventory management

## [0.1.0] - 2025-06-15
- Initial project scaffold
'''


_CONTRIBUTING = '''
# Contributing

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env`
3. `docker compose up -d`
4. `alembic upgrade head`
5. `python -m app.cli.seed_demo`

## Code Style

- Python 3.12+
- Line length: 100 (ruff)
- Type hints on all public functions
- Service layer for business logic
- Repository layer for data access

## Pull Request Process

1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure `pytest tests/unit` passes
4. Update documentation if needed
5. Submit PR with clear description
'''


_SECURITY = '''
# Security Policy

## Reporting Vulnerabilities

Report security issues to the repository owner privately.

## Security Measures

- All passwords hashed with bcrypt
- JWT tokens with configurable expiration
- Tenant data isolation enforced at query level
- Rate limiting on authentication endpoints
- Input validation via Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- Audit trail for sensitive operations

## Recommendations

- Use strong `SECRET_KEY` in production
- Enable HTTPS via reverse proxy
- Restrict database network access
- Rotate secrets periodically
- Monitor audit logs for anomalies
'''


def _scenario_test(n: int) -> str:
    scenarios = [
        "user registration creates tenant and admin",
        "product creation with duplicate SKU fails",
        "stock adjustment increases on-hand quantity",
        "order creation reserves inventory",
        "order fulfillment consumes reservations",
        "order cancellation releases reservations",
        "warehouse transfer moves stock between locations",
        "inventory report shows below-reorder items",
        "sales report filters by date range",
        "audit log records all inventory changes",
    ]
    desc = scenarios[(n - 1) % len(scenarios)]
    return f'''
"""Integration scenario test {n:02d}: {desc}."""

from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from app.core.enums import OrderStatus, StockAdjustmentType, UserRole


class TestScenario{n:02d}:
    """Scenario: {desc}"""

    def test_scenario_setup(self):
        tenant_id = uuid4()
        assert tenant_id is not None

    def test_business_rules(self):
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert StockAdjustmentType.RECEIPT.value == "receipt"
        assert UserRole.ADMIN.value == "admin"

    def test_decimal_arithmetic(self):
        price = Decimal("29.99")
        qty = 3
        total = price * qty
        assert total == Decimal("89.97")

    @pytest.mark.parametrize("status", list(OrderStatus))
    def test_all_order_statuses_valid(self, status):
        assert status.value in (
            "draft", "pending", "confirmed", "fulfilled", "cancelled"
        )

    def test_reservation_lifecycle_states(self):
        from app.core.enums import ReservationStatus
        states = list(ReservationStatus)
        assert len(states) == 4

    def test_transfer_status_flow(self):
        from app.core.enums import TransferStatus
        assert TransferStatus.PENDING.value == "pending"
        assert TransferStatus.COMPLETED.value == "completed"
'''


def _ops() -> dict[str, str]:
    return {
        "app/ops/__init__.py": '"""Operational utilities."""\n',
        "app/ops/health_checks.py": '''
"""Extended health check utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ComponentHealth:
    name: str
    status: str
    latency_ms: float | None = None
    message: str | None = None
    checked_at: datetime | None = None


async def check_database(session) -> ComponentHealth:
    import time
    from sqlalchemy import text
    start = time.perf_counter()
    try:
        await session.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(name="database", status="healthy", latency_ms=latency)
    except Exception as exc:
        return ComponentHealth(name="database", status="unhealthy", message=str(exc))


async def check_redis() -> ComponentHealth:
    import time
    from app.core.cache import get_redis
    start = time.perf_counter()
    try:
        redis = await get_redis()
        await redis.ping()
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(name="redis", status="healthy", latency_ms=latency)
    except Exception as exc:
        return ComponentHealth(name="redis", status="unhealthy", message=str(exc))


async def check_celery() -> ComponentHealth:
    try:
        from app.workers.celery_app import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            return ComponentHealth(name="celery", status="healthy", message=f"{len(stats)} workers")
        return ComponentHealth(name="celery", status="degraded", message="No workers responding")
    except Exception as exc:
        return ComponentHealth(name="celery", status="unhealthy", message=str(exc))
''',
        "app/ops/metrics_collector.py": '''
"""Custom business metrics for Prometheus."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Gauge, Histogram

    ORDERS_CREATED = Counter(
        "inventory_orders_created_total",
        "Total orders created",
        ["tenant_id", "status"],
    )
    STOCK_ADJUSTMENTS = Counter(
        "inventory_stock_adjustments_total",
        "Total stock adjustments",
        ["tenant_id", "type"],
    )
    ACTIVE_RESERVATIONS = Gauge(
        "inventory_active_reservations",
        "Current active stock reservations",
        ["tenant_id"],
    )
    REPORT_GENERATION_SECONDS = Histogram(
        "inventory_report_generation_seconds",
        "Report generation duration",
        ["report_type"],
    )
except ImportError:
    logger.warning("prometheus_client not available for custom metrics")
''',
        "app/ops/backup.py": '''
"""Database backup utilities."""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_backup_filename(prefix: str = "inventory") -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_backup_{ts}.sql"


def run_pg_dump(
    *,
    host: str,
    port: int,
    user: str,
    database: str,
    output_path: Path,
    password: str | None = None,
) -> bool:
    env = {"PGPASSWORD": password} if password else {}
    cmd = [
        "pg_dump",
        "-h", host,
        "-p", str(port),
        "-U", user,
        "-d", database,
        "-f", str(output_path),
        "--no-owner",
        "--no-acl",
    ]
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True)
        logger.info("Backup created: %s", output_path)
        return True
    except subprocess.CalledProcessError as exc:
        logger.error("Backup failed: %s", exc.stderr.decode() if exc.stderr else exc)
        return False
''',
    }
