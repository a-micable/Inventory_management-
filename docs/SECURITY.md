# Security Policy

## Reporting Vulnerabilities

Report security issues to the repository owner privately.

## Security Measures

- All passwords hashed with bcrypt
- JWT tokens with configurable expiration
- Tenant data isolation enforced at query level
- Rate limiting on authentication endpoints
- Input validation via Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- Audit trail for sensitive operations

## Recommendations

- Use strong `SECRET_KEY` in production
- Enable HTTPS via reverse proxy
- Restrict database network access
- Rotate secrets periodically
- Monitor audit logs for anomalies
