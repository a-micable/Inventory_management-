"""Generate Docker configuration files."""

from __future__ import annotations


def generate() -> dict[str, str]:
    return {
        "Dockerfile": _DOCKERFILE,
        "docker-compose.yml": _COMPOSE,
        "docker-compose.test.yml": _COMPOSE_TEST,
        "Makefile": _MAKEFILE,
        ".github/workflows/ci.yml": _CI,
        "docs/ARCHITECTURE.md": _ARCHITECTURE,
        "docs/API.md": _API_DOCS,
        "docs/DEPLOYMENT.md": _DEPLOYMENT,
    }


_DOCKERFILE = '''
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    libpq-dev gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

_COMPOSE = '''
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build: .
    env_file: .env
    depends_on:
      - db
      - redis
    command: celery -A app.workers.celery_app worker --loglevel=info

  beat:
    build: .
    env_file: .env
    depends_on:
      - redis
    command: celery -A app.workers.celery_app beat --loglevel=info

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: inventory
      POSTGRES_PASSWORD: inventory
      POSTGRES_DB: inventory_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U inventory"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
'''

_COMPOSE_TEST = '''
services:
  test-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: inventory_test
    ports:
      - "5433:5432"

  test-redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
'''

_MAKEFILE = '''
.PHONY: up down test migrate seed lint

up:
\tdocker compose up -d

down:
\tdocker compose down

migrate:
\talembic upgrade head

seed:
\tpython -m app.cli.seed_demo

test:
\tpytest tests/ -v --cov=app --cov-report=term-missing

lint:
\truff check app tests
'''

_CI = '''
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: inventory_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/unit -v --cov=app
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/inventory_test
          SYNC_DATABASE_URL: postgresql://test:test@localhost:5432/inventory_test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-for-ci-only
'''

_ARCHITECTURE = '''
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
'''

_API_DOCS = '''
# API Reference

Base URL: `/api/v1`

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register tenant + admin user |
| POST | `/auth/login` | Login and receive JWT tokens |
| POST | `/auth/refresh` | Refresh access token |

## Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | List stock levels |
| POST | `/inventory/adjustments` | Adjust stock quantity |
| POST | `/transfers` | Create warehouse transfer |
| POST | `/transfers/{id}/complete` | Complete transfer |

## Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create order with reservation |
| POST | `/orders/{id}/fulfill` | Fulfill and consume stock |
| POST | `/orders/{id}/cancel` | Cancel and release reservations |
'''

_DEPLOYMENT = '''
# Deployment Guide

## Production Checklist

1. Set strong `SECRET_KEY` (32+ random bytes)
2. Configure PostgreSQL with connection pooling (PgBouncer)
3. Enable Redis persistence for cache and Celery
4. Run migrations: `alembic upgrade head`
5. Deploy API behind reverse proxy (nginx/traefik)
6. Scale Celery workers independently
7. Configure log aggregation (ELK/Datadog)
8. Set up Prometheus scraping on `/metrics`
'''
