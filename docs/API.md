# API Reference

Base URL: `/api/v1`

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register tenant + admin user |
| POST | `/auth/login` | Login and receive JWT tokens |
| POST | `/auth/refresh` | Refresh access token |

## Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | List stock levels |
| POST | `/inventory/adjustments` | Adjust stock quantity |
| POST | `/transfers` | Create warehouse transfer |
| POST | `/transfers/{id}/complete` | Complete transfer |

## Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create order with reservation |
| POST | `/orders/{id}/fulfill` | Fulfill and consume stock |
| POST | `/orders/{id}/cancel` | Cancel and release reservations |
