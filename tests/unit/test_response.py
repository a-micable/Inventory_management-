"""Unit tests for response helpers."""

from __future__ import annotations

from app.utils.response import error_response, success_response


class TestResponses:
    def test_success(self):
        resp = success_response({"id": 1})
        assert resp["success"] is True
        assert resp["data"]["id"] == 1

    def test_error(self):
        resp = error_response("failed", code="test_error", details={"field": "x"})
        assert resp["success"] is False
        assert resp["code"] == "test_error"
