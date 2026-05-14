# Operations Runbook

## Incident Response

### API Down
1. Check `/health` endpoint
2. Verify PostgreSQL connectivity: `docker compose exec db pg_isready`
3. Check Redis: `docker compose exec redis redis-cli ping`
4. Review API logs for exceptions

### High Error Rate
1. Check Prometheus metrics at `/metrics`
2. Review recent deployments
3. Check database connection pool exhaustion
4. Verify Celery worker health

### Stock Discrepancies
1. Query audit logs for recent adjustments
2. Check active reservations: `stock_reservations` where status='active'
3. Review pending transfers
4. Run inventory report with `include_zero_stock=true`

## Maintenance Tasks

### Daily
- Monitor Celery beat schedule execution
- Review error logs
- Check disk usage on PostgreSQL volume

### Weekly
- Review low stock alerts
- Verify backup integrity
- Check audit log growth

### Monthly
- Rotate application secrets
- Review RBAC assignments
- Performance baseline comparison
