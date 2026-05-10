# Monitoring & Observability

## Metrics

Prometheus metrics exposed at `/metrics`:
- HTTP request duration histograms
- Request count by status code
- In-flight requests

## Health Checks

- `GET /health` — Liveness probe
- `GET /ready` — Readiness (DB + Redis connectivity)

## Logging

Structured JSON logs with fields:
- `timestamp`, `level`, `message`
- `tenant_id`, `user_id` (when available)
- `request_id` correlation
