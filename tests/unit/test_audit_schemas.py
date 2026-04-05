"""Unit tests for audit schemas."""

from __future__ import annotations

from app.core.enums import AuditAction, AuditEntityType
from app.schemas.audit import AuditLogFilter


class TestAuditSchemas:
    def test_filter_defaults(self):
        f = AuditLogFilter()
        assert f.entity_type is None
        assert f.action is None
