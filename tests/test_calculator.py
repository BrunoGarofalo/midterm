import pytest
from unittest.mock import MagicMock, patch
from app.calculator import Calculator
from app.exceptions import CommandError, OperationError



@pytest.fixture
def calc():
    """Fixture to create a Calculator instance with mocks."""
    with patch("app.calculator.Originator") as MockOriginator, \
         patch("app.calculator.CareTaker") as MockCaretaker, \
         patch("app.calculator.Subject") as MockSubject, \
         patch("app.calculator.LoggingObserver") as MockLogging, \
         patch("app.calculator.AutosaveObserver") as MockAutosave:
        
        originator = MockOriginator.return_value
        caretaker = MockCaretaker.return_value
        subject = MockSubject.return_value
        logging_observer = MockLogging.return_value
        autosave_observer = MockAutosave.return_value

        c = Calculator()
        c.originator = originator
        c.caretaker = caretaker
        c.subject = subject
        c.logging_observer = logging_observer
        c.autosave_observer = autosave_observer
        return c


# -----------------------------
# Command tests
# -----------------------------
def test_show_commands_contains_expected_entries():
    text = Calculator.show_commands()
    assert "G :" in text or "G:" in text
    assert "Addition" in text
    assert isinstance(text, str)


def test_get_operation_code_valid(caplog):
    op_code = Calculator.get_operation_code("G")
    assert op_code == "add"
    assert "✅ Determined operation code" in caplog.text


def test_get_operation_code_invalid():
    with pytest.raises(CommandError):
        Calculator.get_operation_code("Z")


# -----------------------------
# Operation creation tests
# -----------------------------
@patch("app.calculator.CommandFactory")
def test_create_operation_success(mock_factory, calc):
    operation_obj = MagicMock()
    mock_factory.return_value.createOperationObject.return_value = operation_obj

    result = calc.create_operation("add")
    assert result == operation_obj
    mock_factory.assert_called_once_with("add")


@patch("app.calculator.CommandFactory", side_effect=Exception("Factory fail"))
def test_create_operation_failure(mock_factory, calc):
    with pytest.raises(OperationError):
        calc.create_operation("invalid")


# -----------------------------
# History, undo, redo
# -----------------------------
def test_add_operation_saves_and_notifies(calc):
    calc.originator.create_memento.return_value = "memento"
    calc.add_operation("5 + 5 = 10")
    
    calc.caretaker.save_memento.assert_called_once_with("memento")
    calc.originator.add_operation.assert_called_once_with("5 + 5 = 10")
    calc.subject.notify.assert_called_once_with("5 + 5 = 10")


def test_undo_calls_caretaker(calc):
    calc.undo()
    calc.caretaker.undo_memento.assert_called_once_with(calc.originator)


def test_redo_calls_caretaker(calc):
    calc.redo()
    calc.caretaker.redo_memento.assert_called_once_with(calc.originator)


# -----------------------------
# Show & Delete history
# -----------------------------
def test_show_history_prints(monkeypatch, calc):
    calc.originator.history = ["2 + 2 = 4", "3 * 3 = 9"]
    printed = []
    monkeypatch.setattr("builtins.print", lambda s: printed.append(s))

    calc.show_history()
    assert "2 + 2 = 4" in printed and "3 * 3 = 9" in printed


def test_show_history_warns_when_empty(caplog, calc):
    calc.originator.history = []
    with caplog.at_level("WARNING"):
        calc.show_history()
    assert "Attempted to display history but it is empty" in caplog.text





# def test_delete_history_clears(calc):
#     calc.originator.history = ["5 + 2 = 7", "3 * 4 = 12"]

#     with patch("builtins.input", return_value="Y"):
#         calc.delete_history()

#     # History should now be empty
#     assert calc.originator.history == []



# -----------------------------
# Save & Load
# -----------------------------
def test_save_history_calls_caretaker(calc):
    calc.originator.history = ["a", "b"]
    with patch.object(calc.caretaker, "save_history_to_csv") as mock_save:
        calc.save_history()
        mock_save.assert_called_once_with(calc.originator)


def test_load_history_restores(calc):
    # Mock caretaker's get_loaded_history
    calc.caretaker.get_loaded_history = MagicMock()
    
    # Ensure originator has empty history so load_history can proceed
    calc.originator.history = []
    
    # Call load_history
    calc.load_history()
    
    # Assert caretaker method was called with originator
    calc.caretaker.get_loaded_history.assert_called_once_with(calc.originator)


def test_clear_history_calls_originator(calc):
    calc.clear_history()
    calc.originator.delete_history.assert_called_once()
