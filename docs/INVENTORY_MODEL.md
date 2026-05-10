# Inventory Data Model

## Entities

### InventoryItem
- Unique per (tenant, product, warehouse)
- `quantity_on_hand` — physical stock
- `quantity_reserved` — allocated to orders
- `quantity_available` — on_hand - reserved

### StockAdjustment
- Immutable record of every quantity change
- Types: receipt, damage, correction, return, cycle_count

### StockReservation
- Links order to inventory item
- Status: active → consumed | released | expired
- TTL: 24 hours default

### StockTransfer
- Moves stock between warehouses
- Status: pending → completed
- Creates paired adjustments on completion
