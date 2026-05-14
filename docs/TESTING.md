# Testing Guide

## Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

## Test Structure

- `tests/unit/` — Pure logic, no database
- `tests/integration/` — API and service integration
- `tests/factories.py` — Test data builders
- `tests/helpers.py` — Auth and assertion helpers

## CI

GitHub Actions runs unit tests against PostgreSQL and Redis service containers.
