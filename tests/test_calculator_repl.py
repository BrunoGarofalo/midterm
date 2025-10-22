import pytest
from unittest.mock import MagicMock, patch
from app.calculator_repl import main
import threading
from app.exceptions import CommandError, ValidationError, OperationError, HistoryError


# -------------------------------
# Fixture for mock Calculator
# -------------------------------
@pytest.fixture
def mock_calc():
    calc = MagicMock()
    calc.show_commands.return_value = "A: Add\nB: Subtract"
    calc.get_operation_code.return_value = "add"
    calc.create_operation.return_value.__class__.__name__ = "Addition"
    calc.create_operation.return_value.calculate.return_value = 10
    return calc

# -------------------------------
# Helper to safely run REPL in thread
# -------------------------------
def run_repl_threaded(mock_calc, commands):
    commands_iter = iter(commands)

    def fake_input(prompt):
        try:
            return next(commands_iter)
        except StopIteration:
            raise SystemExit  # exit REPL

    def target():
        with patch("builtins.input", fake_input), \
             patch("app.calculator_repl.Calculator", return_value=mock_calc), \
             patch("builtins.print"):  # suppress print
            try:
                main()
            except SystemExit:
                pass

    t = threading.Thread(target=target)
    t.start()
    t.join(timeout=2)  # prevent freeze
    if t.is_alive():
        t.join()  # force cleanup


# -------------------------------
# REPL command tests
# -------------------------------
def test_help_command_shows_commands(mock_calc):
    run_repl_threaded(mock_calc, ["HELP", "Q"])
    mock_calc.show_commands.assert_called_once()


@pytest.mark.parametrize(
    "command, method_name, op_code",
    [
        ("Q", "delete_history", "exit"),  # exit
        ("L", "delete_history", "clear"),  # clear
        ("O", "save_history", "save"),     # save
        ("P", "load_history", "load"),     # load
        ("K", "show_history", "hist"),     # history
    ]
)
def test_repl_commands_call_methods(mock_calc, command, method_name, op_code):
    mock_calc.get_operation_code.return_value = op_code
    run_repl_threaded(mock_calc, [command])
    getattr(mock_calc, method_name).assert_called_once()


def test_undo_and_redo(mock_calc):
    mock_calc.get_operation_code.side_effect = ["undo", "redo"]
    run_repl_threaded(mock_calc, ["M", "N"])
    mock_calc.undo.assert_called_once()
    mock_calc.redo.assert_called_once()


@patch("app.calculator_repl.get_validated_operand", side_effect=[5, 2])
def test_add_operation_performed(mock_operand, mock_calc):
    mock_calc.get_operation_code.return_value = "add"
    run_repl_threaded(mock_calc, ["G"])
    mock_calc.create_operation.assert_called_once()


@patch("app.calculator_repl.get_validated_operand", side_effect=ValidationError("bad input"))
def test_validation_error_handled(mock_operand, mock_calc):
    mock_calc.get_operation_code.return_value = "add"
    run_repl_threaded(mock_calc, ["G"])  # should not freeze


def test_command_error_handled(mock_calc):
    mock_calc.get_operation_code.side_effect = CommandError("Invalid command")
    run_repl_threaded(mock_calc, ["Z"])  # should not freeze


def test_operation_error_handled(mock_calc):
    mock_calc.get_operation_code.return_value = "add"
    mock_calc.create_operation.side_effect = OperationError("Bad op")
    run_repl_threaded(mock_calc, ["G"])  # should not freeze


def test_history_error_handled(mock_calc):
    mock_calc.get_operation_code.return_value = "undo"
    mock_calc.undo.side_effect = HistoryError("Nothing to undo")
    run_repl_threaded(mock_calc, ["M"])  # should not freeze