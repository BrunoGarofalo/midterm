import pytest
from decimal import Decimal
from app.memento import MementoCalculator, Originator, CareTaker
from app.exceptions import HistoryError
from unittest.mock import patch, MagicMock
from unittest.mock import Mock
from colorama import Fore, Style
from app.exceptions import DataFormatError

# -------------------------------
# MementoCalculator tests
# -------------------------------
def test_redo_memento_raises_historyerror(caplog):
    caretaker = CareTaker()

    # Simulate having something in redo stack
    caretaker.stack_redo = MagicMock()
    caretaker.stack_redo.pop.side_effect = Exception("pop failed")

    # Mock an originator
    originator = MagicMock()

    # Patch logger so we can verify it was called
    with patch("app.memento.logger") as mock_logger:
        with pytest.raises(HistoryError) as exc_info:
            caretaker.redo_memento(originator)

        # Assertions
        assert "Redo failed" in str(exc_info.value)
        mock_logger.exception.assert_called_once()
        assert "pop failed" in mock_logger.exception.call_args[0][0]
        
def test_undo_memento_raises_historyerror(caplog):
    caretaker = CareTaker()

    # Mock stack_undo to simulate having items to pop
    caretaker.stack_undo = MagicMock()
    caretaker.stack_undo.pop.side_effect = Exception("pop failed")  # force an error

    # Mock an originator
    originator = MagicMock()

    # Patch logger to verify logging
    with patch("app.memento.logger") as mock_logger:
        with pytest.raises(HistoryError) as exc_info:
            caretaker.undo_memento(originator)

        # Assertions
        assert "Undo failed" in str(exc_info.value)
        mock_logger.exception.assert_called_once()
        assert "pop failed" in mock_logger.exception.call_args[0][0]

def test_save_memento_raises_historyerror(caplog):
    caretaker = CareTaker()
    caretaker.stack_undo = MagicMock()  # Replace list with mock that will fail

    caretaker.stack_undo.append.side_effect = Exception("append failed")

    with caplog.at_level("ERROR"):
        with pytest.raises(HistoryError) as exc_info:
            caretaker.save_memento(MagicMock())

    # The raised exception should be a HistoryError
    assert "Failed to save memento" in str(exc_info.value)

    # Check that logger.exception was called
    assert any("append failed" in rec.message for rec in caplog.records)
    assert any("Failed to save memento" in rec.message for rec in caplog.records)

def test_get_loaded_history_warns_when_no_csv_history(caplog):
    originator = Originator()

    # Use caplog to capture logger output and patch print to avoid console clutter
    with caplog.at_level("WARNING"), patch("builtins.print") as mock_print:
        originator.get_loaded_history(None)

    # Verify correct warning message logged
    assert any("no history to load" in rec.message.lower() for rec in caplog.records)

    # Verify print was called with correct colored output
    mock_print.assert_called_once()
    printed_msg = mock_print.call_args[0][0]
    assert "No history to load from CSV" in printed_msg

def test_get_loaded_history_raises_dataformaterror(caplog):
    originator = Originator()

    # Create a mock object that raises when copy is called
    mock_list = Mock()
    mock_list.copy.side_effect = Exception("copy failed")

    with caplog.at_level("ERROR"):
        with pytest.raises(DataFormatError) as exc_info:
            originator.get_loaded_history(mock_list)

    # Exception message should include "Failed to load history"
    assert "Failed to load history" in str(exc_info.value)
    assert "copy failed" in str(exc_info.value)

    # Logger should have captured the exception
    assert any("Failed to load history into instance" in rec.message for rec in caplog.records)

def test_delete_history_when_empty(capsys, caplog):
    # Arrange
    originator = Originator()  # empty history by default
    assert originator.history == []

    # Act
    with caplog.at_level("WARNING"):
        originator.delete_history()

    # Capture printed output
    captured = capsys.readouterr()

    # Assert console output contains the expected message
    assert "No instance history to clear" in captured.out
    assert f"{Fore.MAGENTA} No instance history to clear!{Style.RESET_ALL}" in captured.out

    # Assert a warning was logged
    assert any("no history to clear" in rec.message for rec in caplog.records)

def test_memento_creation_and_get_state():
    state = ["5 + 2 = 7", "3 * 4 = 12"]
    memento = MementoCalculator(state)
    # Ensure state is copied, not referenced
    assert memento.get_state() == state
    assert memento.get_state() is not state  # deepcopy ensures different object

# -------------------------------
# Originator tests
# -------------------------------
def test_show_history_displays_entries(capsys, caplog):
    # Arrange
    originator = Originator()
    originator.history = ["5 + 2 = 7", "3 * 4 = 12", "10 - 1 = 9"]

    # Act
    with caplog.at_level("INFO"):
        originator.show_history()

    # Capture printed output
    captured = capsys.readouterr()
    
    # Assert printed output contains each history entry
    for entry in originator.history:
        assert entry in captured.out
        assert f"{Fore.YELLOW}{entry}{Style.RESET_ALL}" in captured.out

    # Assert logger recorded the info
    assert any("History successfully displayed!" in rec.message for rec in caplog.records)
def test_originator_add_and_create_memento():
    originator = Originator()
    originator.add_operation("5 + 2 = 7")
    memento = originator.create_memento()
    assert memento.get_state() == ["5 + 2 = 7"]

def test_originator_create_memento_exception():
    originator = Originator()
    
    # Patch MementoCalculator to raise HistoryError when instantiated
    with patch("app.memento.MementoCalculator", side_effect=HistoryError("memento creation failed")):
        with pytest.raises(HistoryError) as excinfo:
            originator.create_memento()
    
    assert "memento creation failed" in str(excinfo.value)

def test_add_operation_exception():
    originator = Originator()
    # Replace history with a mock object
    originator.history = Mock()
    originator.history.append.side_effect = Exception("append failed")
    
    with pytest.raises(HistoryError) as excinfo:
        originator.add_operation("5 + 2 = 7")
    
    assert "append failed" in str(excinfo.value)

def test_restore_memento_exception():
    originator = Originator()
    
    # Create a mock memento whose get_state method raises an exception
    mock_memento = Mock()
    mock_memento.get_state.side_effect = Exception("Failed to get state")
    
    with pytest.raises(HistoryError) as excinfo:
        originator.restore_memento(mock_memento)
    
    assert "Failed to restore memento" in str(excinfo.value)
    assert "Failed to get state" in str(excinfo.value)

def test_originator_restore_memento():
    originator = Originator()
    originator.add_operation("5 + 2 = 7")
    memento = originator.create_memento()
    originator.add_operation("3 * 4 = 12")
    originator.restore_memento(memento)
    assert originator.history == ["5 + 2 = 7"]

def test_originator_show_and_delete_history(capsys):
    originator = Originator()
    # Show empty history
    originator.show_history()
    captured = capsys.readouterr()
    assert "No history to display" in captured.out
    # Add operation and delete
    originator.add_operation("5 + 2 = 7")
    originator.delete_history()
    assert originator.history == []

def test_originator_get_loaded_history(capsys):
    originator = Originator()
    CSV_history = ["1+1=2", "2*2=4"]
    originator.get_loaded_history(CSV_history)
    assert originator.history == CSV_history
    captured = capsys.readouterr()
    assert "History loaded into instance successfully" in captured.out

# -------------------------------
# CareTaker tests
# -------------------------------
def test_caretaker_undo_redo():
    originator = Originator()
    caretaker = CareTaker()
    
    # Add first operation, saving memento automatically
    originator.add_operation("5 + 2 = 7", caretaker=caretaker)

    # Add second operation, saving memento automatically
    originator.add_operation("3 * 4 = 12", caretaker=caretaker)

    # Undo last operation
    undone_op = caretaker.undo_memento(originator)
    assert originator.history == ["5 + 2 = 7"]
    assert undone_op == "3 * 4 = 12"

    # Redo last operation
    redone_op = caretaker.redo_memento(originator)
    assert originator.history == ["5 + 2 = 7", "3 * 4 = 12"]
    assert redone_op == "3 * 4 = 12"

def test_undo_without_history(capsys):
    originator = Originator()
    caretaker = CareTaker()
    result = caretaker.undo_memento(originator)
    captured = capsys.readouterr()
    assert result is None
    assert "No operation to undo" in captured.out

def test_redo_without_history(capsys):
    originator = Originator()
    caretaker = CareTaker()
    result = caretaker.redo_memento(originator)
    captured = capsys.readouterr()
    assert result is False
    assert "No operation to redo" in captured.out

def test_save_memento_clears_redo_stack():
    originator = Originator()
    caretaker = CareTaker()
    originator.add_operation("5 + 2 = 7")
    m = originator.create_memento()
    caretaker.stack_redo.append(originator.create_memento())  # pre-fill redo
    caretaker.save_memento(m)
    assert len(caretaker.stack_redo) == 0

# -------------------------------
# Memento calculator tests
# -------------------------------
def test_mementocalculator_init_exception():
    state = ["5 + 2 = 7", "3 * 4 = 12"]
    
    # Patch deepcopy to raise an exception
    with patch("app.memento.deepcopy", side_effect=Exception("deepcopy failed")):
        with pytest.raises(HistoryError) as excinfo:
            MementoCalculator(state)
    
    assert "Failed to create memento" in str(excinfo.value)

def test_mementocalculator_get_state_exception():
    state = ["5 + 2 = 7", "3 * 4 = 12"]
    memento = MementoCalculator(state)
    
    # Patch deepcopy to raise an exception when get_state is called
    with patch("app.memento.deepcopy", side_effect=Exception("deepcopy failed")):
        with pytest.raises(HistoryError) as excinfo:
            memento.get_state()
    
    assert "Failed to get memento state" in str(excinfo.value)