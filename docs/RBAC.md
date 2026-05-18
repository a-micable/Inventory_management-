# Role-Based Access Control

## Roles

| Role | Description |
|------|-------------|
| Admin | Full access including user management and audit logs |
| Manager | Inventory, orders, warehouses, reports |
| Employee | Read inventory, create orders |

## Permission Matrix

| Permission | Admin | Manager | Employee |
|------------|-------|---------|----------|
| users:read | ✓ | ✓ | ✗ |
| users:write | ✓ | ✗ | ✗ |
| products:read | ✓ | ✓ | ✓ |
| products:write | ✓ | ✓ | ✗ |
| inventory:adjust | ✓ | ✓ | ✗ |
| orders:create | ✓ | ✓ | ✓ |
| orders:fulfill | ✓ | ✓ | ✗ |
| reports:read | ✓ | ✓ | ✗ |
| audit:read | ✓ | ✗ | ✗ |
