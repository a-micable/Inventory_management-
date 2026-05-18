# Multi-Tenancy Design

## Isolation Strategy

Row-level isolation via `tenant_id` on all business tables.

## Tenant Resolution

1. JWT `tenant_id` claim (primary)
2. `X-Tenant-ID` + `X-Tenant-Slug` headers (middleware)
3. Login requires `tenant_slug` parameter

## Data Access Rules

- All repository queries MUST filter by `tenant_id`
- Cross-tenant access is prevented at service layer
- Audit logs are tenant-scoped
