import pytest
from app.command_factory import CommandFactory
from app.calculation import (
    Percentage, IntegerDivision, Modulo, Root, Absdifference,
    Multiplication, Addition, Division, Subtraction, Power,
    CalculationTemplate
)
from app.exceptions import CommandError

@pytest.mark.parametrize("user_input, expected_class", [
    ("percentage", Percentage),
    ("add", Addition),
    ("subtract", Subtraction),
    ("div", Division),
    ("intdiff", IntegerDivision),
    ("modulo", Modulo),
    ("root", Root),
    ("absdiff", Absdifference),
    ("multiplication", Multiplication),
    ("power", Power),
])
def test_create_operation_object_valid(user_input, expected_class):
    factory = CommandFactory(user_input)
    op = factory.createOperationObject()
    assert isinstance(op, expected_class)

def test_create_operation_object_invalid():
    factory = CommandFactory("invalid_command")
    with pytest.raises(CommandError) as exc_info:
        factory.createOperationObject()
    assert "Command 'invalid_command' not allowed" in str(exc_info.value)
    # Also check that allowed commands are listed
    for cmd in CalculationTemplate.operations_allowed:
        assert cmd in str(exc_info.value)

def test_factory_user_input_is_stored():
    factory = CommandFactory("add")
    assert factory.user_input == "add"
