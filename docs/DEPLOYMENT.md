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
