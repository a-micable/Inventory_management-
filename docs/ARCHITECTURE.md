# Architecture Overview

## Layered Design

```
┌─────────────────────────────────────────────┐
│              API Routers                     │
│  auth · users · products · inventory ·       │
│  orders · warehouses · reports · audit       │
├─────────────────────────────────────────────┤
│              Service Layer                   │
│  Business logic, transactions, audit hooks   │
├─────────────────────────────────────────────┤
│            Repository Layer                  │
│  Data access, query composition              │
├─────────────────────────────────────────────┤
│           SQLAlchemy Models                  │
│  PostgreSQL with tenant-scoped isolation     │
└─────────────────────────────────────────────┘
```

## Multi-Tenancy

Every business entity carries a `tenant_id` foreign key. Request context
establishes tenant scope via JWT claims and middleware headers.

## Background Processing

Celery workers handle:
- Async report generation
- Stale reservation expiry
- Inventory cache warming
- Audit log retention purging
