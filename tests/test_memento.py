import pytest
from decimal import Decimal
from app.memento import MementoCalculator, Originator, CareTaker
from app.exceptions import HistoryError
from unittest.mock import patch, MagicMock
from unittest.mock import Mock
from colorama import Fore, Style
from app.exceptions import DataFormatError
import os
from app.config import CALCULATOR_MAX_HISTORY_SIZE, CSV_COLUMNS, CALCULATOR_HISTORY_DIR
import pandas as pd

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
    caretaker = CareTaker()

    # Ensure CSV file does not exist
    if caretaker.log_file and os.path.exists(caretaker.log_file):
        os.remove(caretaker.log_file)

    # Capture logger output and patch print
    with caplog.at_level("WARNING"), patch("builtins.print") as mock_print:
        caretaker.get_loaded_history(originator)

    # Verify log warning was produced
    assert any("No CSV history file found" in record.message for record in caplog.records)
    # Verify print message was called
    mock_print.assert_called()

   # Mock the file checks so that the code attempts to read the CSV
    with patch("os.path.exists", return_value=True), \
         patch("os.path.getsize", return_value=1), \
         patch("pandas.read_csv", side_effect=Exception("read_csv failed")):

        with caplog.at_level("ERROR"):
            with pytest.raises(DataFormatError) as exc_info:
                caretaker.get_loaded_history(originator)

    assert any("Failed to load history from CSV" in record.message for record in caplog.records)


def test_memento_creation_and_get_state():
    state = ["5 + 2 = 7", "3 * 4 = 12"]
    memento = MementoCalculator(state)
    # Ensure state is copied, not referenced
    assert memento.get_state() == state
    assert memento.get_state() is not state  # deepcopy ensures different object

# -------------------------------
# Originator tests
# -------------------------------
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

def test_add_operation_trims_history(monkeypatch, caplog):
    originator = Originator()

    # Create dummy operations exceeding the max history size
    total_ops = CALCULATOR_MAX_HISTORY_SIZE + 5
    dummy_operations = [f"{i} + 1 = {i+1}" for i in range(total_ops)]

    # Patch logger to capture info messages
    with caplog.at_level("INFO"):
        for op in dummy_operations:
            originator.add_operation(op)

    # History length should equal the max allowed size
    assert len(originator.history) == CALCULATOR_MAX_HISTORY_SIZE

    # The retained operations should be the most recent ones
    expected_history = dummy_operations[-CALCULATOR_MAX_HISTORY_SIZE:]
    assert originator.history == expected_history

    # There should be a log about trimming
    assert any("History exceeded max size" in record.message for record in caplog.records)

def test_get_loaded_history_reads_csv_and_updates_originator(monkeypatch, caplog):
    originator = Originator()
    caretaker = CareTaker()

    # Dummy CSV data
    csv_data = pd.DataFrame([
        {"timestamp": "2025-10-23 12:00", "operation": "add", "operand1": "2", "operand2": "3", "result": "5", "instance_id": "1"},
        {"timestamp": "2025-10-23 12:01", "operation": "multiply", "operand1": "3", "operand2": "4", "result": "12", "instance_id": "1"}
    ], columns=CSV_COLUMNS)

    with patch("os.path.exists", return_value=True), \
         patch("os.path.getsize", return_value=1), \
         patch("pandas.read_csv", return_value=csv_data):

        with patch.object(Originator, "add_operation", wraps=originator.add_operation) as mock_add_op:
            with caplog.at_level("INFO"):
                caretaker.get_loaded_history(originator)

    # Now add_operation should have been called for each CSV row
    assert mock_add_op.call_count == len(csv_data)
    assert len(originator.history) == len(csv_data)

    # Logs should indicate successful load
    assert any("History loaded into instance successfully" in record.message for record in caplog.records)
    assert any(f"Loaded {len(csv_data)} operations" in record.message for record in caplog.records)

def test_save_history_to_csv_saves_valid_entries(monkeypatch, caplog):
    originator = Originator()
    caretaker = CareTaker()

    # Prepare history with two valid entries and one malformed
    originator.history = [
        "2025-10-23 12:00,add,2,3,5,1",
        "2025-10-23 12:01,multiply,3,4,12,1",
        "malformed entry without proper columns"
    ]

    # Patch os.makedirs to avoid actually creating directories
    with patch("os.makedirs") as mock_makedirs, \
         patch("pandas.DataFrame.to_csv") as mock_to_csv:
        with caplog.at_level("INFO"):
            caretaker.save_history_to_csv(originator)

    # Check that the directory creation was called
    mock_makedirs.assert_called_once_with(CALCULATOR_HISTORY_DIR, exist_ok=True)

    # Only 2 valid entries should be written
    mock_to_csv.assert_called_once()
    args, kwargs = mock_to_csv.call_args
    df_passed = args[0] if args else kwargs.get("index", None)
    # Actually test dataframe rows passed
    # Can't get df directly from to_csv mock, but can check logger
    assert any("Saved 2 operations to CSV" in record.message for record in caplog.records)
    assert any("Skipping unproperly formatted entry" in record.message for record in caplog.records)

def test_save_history_to_csv_no_history(caplog):
    originator = Originator()
    caretaker = CareTaker()

    # history is empty
    originator.history = []

    with caplog.at_level("WARNING"):
        caretaker.save_history_to_csv(originator)

    # Ensure no CSV attempt
    assert any("No history to save!" in record.message for record in caplog.records)

def test_delete_saved_history_file_exists(monkeypatch, caplog):
    originator = Originator()
    originator.history = ["op1", "op2"]
    caretaker = CareTaker()

    # Patch os.path.exists to simulate CSV file existing
    with patch("os.path.exists", return_value=True), \
         patch("os.remove") as mock_remove:
        with caplog.at_level("INFO"):
            caretaker.delete_saved_history(originator)

    # Check file deletion called
    mock_remove.assert_called_once_with(caretaker.log_file)

    # Check originator history cleared
    assert originator.history == []

    # Check undo/redo stacks cleared
    assert caretaker.stack_undo == []
    assert caretaker.stack_redo == []

    # Check logs
    assert any("Deleted saved history file" in record.message for record in caplog.records)
    assert any("Deleted in-memory history" in record.message for record in caplog.records)

def test_delete_saved_history_file_missing(monkeypatch, caplog):
    originator = Originator()
    originator.history = ["op1", "op2"]
    caretaker = CareTaker()

    # Simulate file missing
    with patch("os.path.exists", return_value=False), \
         patch("os.remove") as mock_remove:
        with caplog.at_level("WARNING"):
            caretaker.delete_saved_history(originator)

    # File deletion should NOT be called
    mock_remove.assert_not_called()

    # History and stacks still cleared
    assert originator.history == []
    assert caretaker.stack_undo == []
    assert caretaker.stack_redo == []

    # Check warning log
    assert any("No saved history file found" in record.message for record in caplog.records)
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