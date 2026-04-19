.PHONY: up down test migrate seed lint

up:
	docker compose up -d

down:
	docker compose down

migrate:
	alembic upgrade head

seed:
	python -m app.cli.seed_demo

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app tests
