.PHONY: up down test migrate lint

up:
	docker compose up -d


down:
	docker compose down


migrate:
	alembic upgrade head


test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app tests
