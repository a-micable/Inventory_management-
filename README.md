# Enterprise Inventory & Order Management API

Modern FastAPI backend for enterprise inventory, warehouse, and order
operations. Designed for high-throughput multi-tenant deployments with
role-based access control, audit logging, Redis caching, and asynchronous
background processing.

## Architecture

- **API Layer** (`app/routers`) — HTTP endpoint design and request validation
- **Service Layer** (`app/services`) — transaction-aware business workflows
- **Repository Layer** (`app/repositories`) — tenant-aware data access abstraction
- **Domain Models** (`app/models`) — SQLAlchemy ORM entities with audit metadata
- **Workers** (`app/workers`) — asynchronous jobs for reporting and maintenance

## Quick Start

```bash
cp .env.example .env
docker compose up -d
docker compose exec api alembic upgrade head
```

API docs: http://localhost:8000/docs

## Core Capabilities

| Capability | Description |
|------------|-------------|
| Authentication | JWT-based login, refresh tokens, password security |
| Authorization | RBAC for tenants, users, and operational roles |
| Inventory | Stock adjustments, reservations, transfers, warehouse lifecycle |
| Orders | Order creation, fulfillment, cancellation, stock commitment |
| Reporting | Scheduled and on-demand inventory analytics |
| Audit | Immutable action logs with tenant and user traceability |

## Testing

```bash
pytest tests/ -v --cov=app
```
