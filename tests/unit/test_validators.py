"""Unit tests for input validators."""

from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.utils.validators import validate_password, validate_sku


class TestPasswordValidation:
    def test_valid_password(self):
        validate_password("SecurePass1")

    def test_too_short(self):
        with pytest.raises(ValidationError, match="at least"):
            validate_password("Sh0rt")

    def test_missing_uppercase(self):
        with pytest.raises(ValidationError, match="uppercase"):
            validate_password("lowercase1")

    def test_missing_digit(self):
        with pytest.raises(ValidationError, match="digit"):
            validate_password("NoDigitsHere")


class TestSKUValidation:
    def test_valid_sku(self):
        assert validate_sku("sku-001") == "SKU-001"

    def test_invalid_sku(self):
        with pytest.raises(ValidationError):
            validate_sku("ab")
