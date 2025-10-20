import pytest
from decimal import Decimal
from app.calculation import (
    Addition, Subtraction, Multiplication, Division,
    IntegerDivision, Percentage, Power, Root,
    Modulo, Absdifference
)
from app.exceptions import ValidationError, OperationError
from app.config import CALCULATOR_MAX_INPUT_VALUE, CALCULATOR_PRECISION

# Helper function to quantize decimals using config precision
def quantize_decimal(val: Decimal):
    return val.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"))

# ---------------------------------------------------------
# Addition
# ---------------------------------------------------------
def test_addition_basic():
    op = Addition()
    result = op.calculate(Decimal("2"), Decimal("3"))
    assert result == quantize_decimal(Decimal("5"))

# ---------------------------------------------------------
# Subtraction
# ---------------------------------------------------------
def test_subtraction_basic():
    op = Subtraction()
    result = op.calculate(Decimal("5"), Decimal("3"))
    assert result == quantize_decimal(Decimal("2"))

# ---------------------------------------------------------
# Multiplication
# ---------------------------------------------------------
def test_multiplication_basic():
    op = Multiplication()
    result = op.calculate(Decimal("2"), Decimal("3"))
    assert result == quantize_decimal(Decimal("6"))

# ---------------------------------------------------------
# Division
# ---------------------------------------------------------
def test_division_basic():
    op = Division()
    result = op.calculate(Decimal("6"), Decimal("3"))
    assert result == quantize_decimal(Decimal("2"))

def test_division_by_zero():
    op = Division()
    with pytest.raises(OperationError):
        op.calculate(Decimal("5"), Decimal("0"))

# ---------------------------------------------------------
# IntegerDivision
# ---------------------------------------------------------
def test_integer_division_basic():
    op = IntegerDivision()
    result = op.calculate(Decimal("7"), Decimal("2"))
    assert result == 3  # integer division returns int

def test_integer_division_by_zero():
    op = IntegerDivision()
    with pytest.raises(OperationError):
        op.calculate(Decimal("5"), Decimal("0"))

# ---------------------------------------------------------
# Percentage
# ---------------------------------------------------------
def test_percentage_basic():
    op = Percentage()
    result = op.calculate(Decimal("50"), Decimal("200"))
    assert result == 25.0000

def test_percentage_by_zero():
    op = Percentage()
    with pytest.raises(OperationError):
        op.calculate(Decimal("50"), Decimal("0"))

# ---------------------------------------------------------
# Power
# ---------------------------------------------------------
def test_power_basic():
    op = Power()
    result = op.calculate(Decimal("2"), Decimal("3"))
    assert result == quantize_decimal(Decimal("8"))

# # ---------------------------------------------------------
# # Root
# # ---------------------------------------------------------
# def test_root_basic():
#     op = Root()
#     result = op.calculate(Decimal("16"), Decimal("2"))
#     assert result == quantize_decimal(Decimal("4"))

# def test_root_negative_radicand():
#     op = Root()
#     with pytest.raises(ValidationError):
#         op.calculate(Decimal("-16"), Decimal("2"))

# def test_root_zero_degree():
#     op = Root()
#     with pytest.raises(ValidationError):
#         op.calculate(Decimal("16"), Decimal("0"))

# # ---------------------------------------------------------
# # Modulo
# # ---------------------------------------------------------
# def test_modulo_basic():
#     op = Modulo()
#     result = op.calculate(Decimal("10"), Decimal("3"))
#     assert result == quantize_decimal(Decimal("1"))

# def test_modulo_by_zero():
#     op = Modulo()
#     with pytest.raises(ValueError):
#         op.calculate(Decimal("10"), Decimal("0"))

# # ---------------------------------------------------------
# # Absolute Difference
# # ---------------------------------------------------------
# def test_absdifference_basic():
#     op = Absdifference()
#     result = op.calculate(Decimal("5"), Decimal("3"))
#     assert result == quantize_decimal(Decimal("2"))

# # ---------------------------------------------------------
# # Input exceeding max value
# # ---------------------------------------------------------
# def test_check_decimals_exceeds_max():
#     op = Addition()
#     with pytest.raises(ValidationError):
#         op.calculate(CALCULATOR_MAX_INPUT_VALUE + 1, Decimal("1"))
