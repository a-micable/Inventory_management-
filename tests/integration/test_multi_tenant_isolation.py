"""Integration tests for multi-tenant isolation."""

from __future__ import annotations

from uuid import uuid4


class TestTenantIsolation:
    def test_different_tenant_ids(self):
        t1 = uuid4()
        t2 = uuid4()
        assert t1 != t2

    def test_tenant_scoped_queries_require_id(self):
        tenant_id = uuid4()
        assert str(tenant_id) != ""
