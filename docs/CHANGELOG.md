# Changelog

## [1.0.0] - 2026-06-11

### Added
- Multi-tenant inventory and order management platform
- JWT authentication with role-based access control
- Product catalog with SKU management
- Multi-warehouse inventory tracking
- Stock adjustments, reservations, and transfers
- Order lifecycle: create, confirm, fulfill, cancel
- Audit logging for all inventory and order actions
- Inventory and sales report generation
- Redis caching layer
- Celery background workers for reports and maintenance
- Docker Compose development environment
- Comprehensive test suite (unit + integration)
- Prometheus metrics and health probes
- Demo data seeder CLI

### Security
- bcrypt password hashing
- JWT access and refresh tokens
- Rate limiting on authentication endpoints
- Tenant isolation at data layer

## [0.9.0] - 2026-03-15
- Beta release with order processing

## [0.5.0] - 2025-10-01
- Alpha release with inventory management

## [0.1.0] - 2025-06-15
- Initial project scaffold

<!-- 2026-05-04T15:58:08 perf(reports): fix transfer status transition guard -->

<!-- 2026-05-04T18:17:49 style(api): consolidate exception handlers -->

<!-- 2026-05-06T16:49:52 feat(db): improve test factory helpers -->

<!-- 2026-05-07T09:29:08 fix(cache): document RBAC permission matrix -->

<!-- 2026-05-07T14:27:43 refactor(workers): pin fastapi version -->

<!-- 2026-05-07T15:05:42 test(auth): fix tenant context not cleared after request -->

<!-- fix fix:docs @ 2026-05-08 -->

<!-- 2026-05-09T18:41:56 docs: reorganize schema modules by domain -->

<!-- 2026-05-12T20:56:06 chore(orders): add inventory adjustment tests -->

<!-- 2026-05-14T18:49:47 perf(warehouses): add migration guide -->

<!-- 2026-05-15T19:03:18 style(reports): update .gitignore -->

<!-- 2026-05-16T14:39:43 feat(api): fix refresh token type validation -->

<!-- 2026-05-17T18:48:27 fix(db): reorganize schema modules by domain -->

<!-- 2026-05-19T14:17:48 refactor(cache): improve test factory helpers -->

<!-- 2026-05-20T17:44:56 test(workers): add deployment checklist -->

<!-- 2026-05-21T14:39:47 docs: configure pytest asyncio mode -->

<!-- 2026-05-21T16:20:58 chore(inventory): handle missing authorization header gracefully -->

<!-- 2026-05-22T16:08:24 perf(orders): move business logic to service layer -->

<!-- 2026-05-23T20:31:55 style(warehouses): improve test factory helpers -->

<!-- 2026-05-24T15:39:52 feat(reports): document API endpoints -->

<!-- 2026-05-27T11:31:14 fix(api): add .env.example -->

<!-- 2026-05-29T10:34:02 refactor(db): fix tenant context not cleared after request -->

<!-- 2026-05-30T16:28:57 test(cache): extract number generation utilities -->

<!-- 2026-05-31T12:20:47 docs: add schema validation tests -->

<!-- 2026-05-31T12:52:09 chore(auth): add architecture documentation -->

<!-- 2026-05-31T14:25:45 perf(inventory): pin fastapi version -->

<!-- 2026-05-31T15:00:46 style(orders): handle duplicate SKU conflict properly -->

<!-- 2026-06-02T20:24:24 feat(warehouses): reorganize schema modules by domain -->

<!-- 2026-06-04T13:39:20 fix(reports): add inventory adjustment tests -->

<!-- 2026-06-05T09:55:20 refactor(api): document API endpoints -->
