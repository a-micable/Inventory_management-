# Contributing

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env`
3. `docker compose up -d`
4. `docker compose exec api alembic upgrade head`

## Code Style

- Python 3.12+
- Line length: 100 (ruff)
- Type hints on public APIs and services
- Domain-oriented service layer for business logic
- Repository layer for database access

## Pull Request Process

1. Create a feature branch from `main`
2. Add or update tests for new behavior
3. Run `pytest tests/unit` and confirm success
4. Update documentation when requirements or behavior change
5. Submit a PR with a clear summary and scope
