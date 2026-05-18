# Order Processing Workflow

## State Machine

```
DRAFT → PENDING → CONFIRMED → FULFILLED
                  ↓
              CANCELLED
```

## Create Order

1. Validate warehouse and products belong to tenant
2. Calculate line totals and subtotal
3. Create order record with PENDING status
4. Reserve inventory for each line item
5. Transition to CONFIRMED status
6. Log audit event

## Fulfill Order

1. Verify order is in CONFIRMED status
2. Consume all active reservations (deduct on-hand, release reserved)
3. Set status to FULFILLED
4. Record fulfiller ID
5. Log audit event

## Cancel Order

1. Verify order is not FULFILLED or already CANCELLED
2. Release all active reservations
3. Set status to CANCELLED
4. Log audit event with optional reason
