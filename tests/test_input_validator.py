import pytest
from decimal import Decimal, InvalidOperation
from app.input_validators import get_valid_operand, validate_nonzero, validate_nonnegative, get_validated_operand
from app.exceptions import ValidationError
from app.config import CALCULATOR_MAX_INPUT_VALUE

# ---------------------------
# Tests for validate_nonzero
# ---------------------------
def test_validate_nonzero_positive():
    assert validate_nonzero(Decimal("5")) == Decimal("5")


def test_validate_nonzero_zero():
    with pytest.raises(ValidationError) as exc_info:
        validate_nonzero(Decimal("0"), var_name="Denominator")
    assert "Denominator cannot be zero" in str(exc_info.value)


def test_validate_nonzero_negative():
    assert validate_nonzero(Decimal("-10")) == Decimal("-10")


# -------------------------------
# Tests for validate_nonnegative
# -------------------------------
def test_validate_nonnegative_positive():
    assert validate_nonnegative(Decimal("10")) == Decimal("10")


def test_validate_nonnegative_zero():
    assert validate_nonnegative(Decimal("0")) == Decimal("0")


def test_validate_nonnegative_negative():
    with pytest.raises(ValidationError) as exc_info:
        validate_nonnegative(Decimal("-3"), var_name="Radicand")
    assert "Radicand cannot be negative" in str(exc_info.value)


# -------------------------------
# Tests for get_valid_operand
# -------------------------------
def test_get_valid_operand_valid(monkeypatch):
    inputs = iter(["42"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_valid_operand("Enter a number: ")
    assert result == Decimal("42")


def test_get_valid_operand_invalid_then_valid(monkeypatch, caplog):
    # First invalid string input, then valid number
    inputs = iter(["abc", "100"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    caplog.set_level("INFO")
    result = get_valid_operand("Enter a number: ")
    assert result == Decimal("100")
    assert any("Invalid input 'abc'" in rec.message for rec in caplog.records)


def test_get_valid_operand_too_large(monkeypatch, caplog):
    # Input exceeds CALCULATOR_MAX_INPUT_VALUE, then valid input
    too_large = str(Decimal(CALCULATOR_MAX_INPUT_VALUE) + 1)
    valid_value = "500"
    inputs = iter([too_large, valid_value])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    caplog.set_level("WARNING")
    result = get_valid_operand("Enter a number: ")
    assert result == Decimal(valid_value)
    assert any("Value too large" in rec.message for rec in caplog.records)

# -------------------------------
# Tests for get_validated_operand
# -------------------------------
def test_get_validated_operand_single_valid(monkeypatch):
    """Should return the first valid input."""
    inputs = iter(["42"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_validated_operand("Enter a number: ")
    assert result == Decimal("42")


def test_get_validated_operand_retry_invalid(monkeypatch, caplog):
    """Should retry until a valid number is entered."""
    inputs = iter(["abc", "not_a_number", "123.45"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    caplog.set_level("INFO")
    result = get_validated_operand("Enter a number: ")
    assert result == Decimal("123.45")
    # Ensure invalid inputs were logged
    assert any("Invalid input 'abc'" in rec.message for rec in caplog.records)
    assert any("Invalid input 'not_a_number'" in rec.message for rec in caplog.records)