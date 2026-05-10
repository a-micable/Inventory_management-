# Database Migrations

## Running Migrations

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "description"
```

## Migration History

1. `0001` — Tenants and users
2. `0002` — Products and warehouses
3. `0003` — Inventory items and adjustments
4. `0004` — Orders and reservations
5. `0005` — Transfers and audit logs
6. `0006` — Report jobs
