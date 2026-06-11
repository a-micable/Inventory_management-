#!/usr/bin/env python3
"""
Generate the Multi-Tenant Inventory & Order Management Platform codebase.
Produces 50+ Python files and 10,000+ lines of production-style code.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def write(relative_path: str, content: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def generate_all() -> dict[str, str]:
    """Return mapping of relative path -> file content."""
    files: dict[str, str] = {}

    files[".gitignore"] = """
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.env
.env.*
!.env.example
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
dist/
build/
*.log
.DS_Store
.idea/
.vscode/
docker/wheels/
"""

    files[".env.example"] = """
DATABASE_URL=postgresql+asyncpg://inventory:inventory@localhost:5432/inventory_db
SYNC_DATABASE_URL=postgresql://inventory:inventory@localhost:5432/inventory_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
SECRET_KEY=change-me-in-production-use-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
RUN_MIGRATIONS=false
LOG_LEVEL=INFO
DEFAULT_TENANT_SLUG=demo
"""

    files["requirements.txt"] = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.13.0
pydantic-settings==2.1.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.4.0
httpx==0.28.1
pytest==8.4.3
pytest-asyncio==0.23.3
pytest-cov==4.1.0
redis==5.0.1
celery==5.3.4
python-json-logger==2.0.7
python-multipart==0.0.6
slowapi==0.1.9
prometheus-fastapi-instrumentator==6.1.0
email-validator==2.1.0
"""

    files["pyproject.toml"] = """
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "inventory-platform"
version = "1.0.0"
description = "Multi-Tenant Inventory & Order Management Platform"
requires-python = ">=3.11"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
source = ["app"]
omit = ["app/workers/*", "tests/*"]

[tool.ruff]
line-length = 100
target-version = "py312"
"""

    files["README.md"] = textwrap.dedent("""
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
    """)

    # Import all module generators
    from scripts.modules import core, models, schemas, repositories, services, routers
    from scripts.modules import workers, middleware, dependencies, tests, alembic_files, docker_files
    from scripts.modules import expansion, expansion2, expansion3, expansion4

    files.update(core.generate())
    files.update(expansion.generate())
    files.update(expansion2.generate())
    files.update(expansion3.generate())
    files.update(expansion4.generate())
    files.update(models.generate())
    files.update(schemas.generate())
    files.update(repositories.generate())
    files.update(services.generate())
    files.update(routers.generate())
    files.update(workers.generate())
    files.update(middleware.generate())
    files.update(dependencies.generate())
    files.update(tests.generate())
    files.update(alembic_files.generate())
    files.update(docker_files.generate())

    return files


def main() -> None:
    files = generate_all()
    for rel_path, content in sorted(files.items()):
        write(rel_path, content)
    py_files = [p for p in files if p.endswith(".py")]
    total_lines = sum(len(files[p].splitlines()) for p in files)
    print(f"Generated {len(files)} files ({len(py_files)} Python), ~{total_lines:,} lines")


if __name__ == "__main__":
    main()
