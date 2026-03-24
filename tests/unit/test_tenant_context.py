"""Unit tests for tenant context."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.core.exceptions import TenantError
from app.core.tenant_context import (
    TenantContext,
    clear_context,
    get_tenant_context,
    get_tenant_id,
    set_tenant_context,
)


class TestTenantContext:
    def setup_method(self):
        clear_context()

    def test_set_and_get(self):
        tid = uuid4()
        set_tenant_context(TenantContext(tenant_id=tid, tenant_slug="demo"))
        assert get_tenant_id() == tid
        assert get_tenant_context().tenant_slug == "demo"

    def test_missing_context_raises(self):
        with pytest.raises(TenantError):
            get_tenant_context()
