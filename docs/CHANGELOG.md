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
