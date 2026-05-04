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
