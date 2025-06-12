# Multi-Tenant Inventory & Order Management Platform

Production-grade FastAPI backend for multi-tenant inventory, warehouse,
and order management with JWT authentication, RBAC, audit logging, Redis
caching, and Celery background workers.

## Architecture

- **API Layer** (`app/routers`) — HTTP endpoints, request validation
- **Service Layer** (`app/services`) — business logic, transactions
- **Repository Layer** (`app/repositories`) — data access abstraction
- **Models** (`app/models`) — SQLAlchemy ORM entities
- **Workers** (`app/workers`) — async report generation, cache warming

## Quick Start

```bash
cp .env.example .env
docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.cli.seed_demo
```

API docs: http://localhost:8000/docs

## Modules

| Module | Description |
|--------|-------------|
| Users | Registration, login, JWT, roles (Admin/Manager/Employee) |
| Inventory | Products, stock adjustments, reservations, transfers |
| Orders | Create, cancel, fulfill with inventory reservation |
| Warehouses | Multi-warehouse stock and inter-warehouse transfers |
| Reports | Inventory and sales analytics |
| Audit | Immutable action log for inventory and order events |

## Testing

```bash
pytest tests/ -v --cov=app
```
