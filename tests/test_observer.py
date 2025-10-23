import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
from app.observers import LoggingObserver, AutosaveObserver, Subject
from app.exceptions import FileAccessError, HistoryError, DataFormatError
from app.config import CALCULATOR_MAX_HISTORY_SIZE, CALCULATOR_AUTO_SAVE, CALCULATOR_DEFAULT_ENCODING, CALCULATOR_DEFAULT_ENCODING, CSV_COLUMNS
from app.logger import logger
import json


# ----------------------------
# LoggingObserver Tests
# ----------------------------
def test_loggingobserver_init_error(monkeypatch):
    """Simulate os.makedirs failing to raise FileAccessError"""
    monkeypatch.setattr(os, "makedirs", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("mkdir fail")))

    with pytest.raises(FileAccessError):
        LoggingObserver()


def test_loggingobserver_update_empty_message(monkeypatch):
    observer = LoggingObserver()
    with patch.object(logger, "warning") as mock_warn:
        observer.update("")
        mock_warn.assert_called_once()
        assert "Caclulation data unavailable" in mock_warn.call_args[0][0]


def test_loggingobserver_update_success(tmp_path):
    """Ensure JSONL is appended correctly"""
    log_file = tmp_path / "log.jsonl"
    with patch("os.path.join", return_value=str(log_file)):
        observer = LoggingObserver()

    message = {"timestamp": "2025-10-21", "operation": "add", "operand1": 2, "operand2": 3, "result": 5}
    with patch("builtins.open", mock_open()) as m:
        observer.update(message)
        m.assert_called_once_with(observer.log_file, "a", encoding=CALCULATOR_DEFAULT_ENCODING)
        handle = m()
        handle.write.assert_called_once_with(json.dumps(message) + "\n")


def test_loggingobserver_update_write_error(monkeypatch):
    observer = LoggingObserver()
    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(Exception("disk error")))

    with patch.object(logger, "error") as mock_err:
        observer.update({"dummy": "data"})
        mock_err.assert_called_once()
        assert "failed to save" in mock_err.call_args[0][0]


# ----------------------------
# AutosaveObserver Tests
# ----------------------------
def test_autosaveobserver_init_new_file(tmp_path):
    """Should create a new CSV if file missing or empty"""
    log_file = str(tmp_path / "auto.csv")
    with patch("os.path.exists", return_value=False):
        obs = AutosaveObserver(log_file=log_file)
        assert isinstance(obs.df, pd.DataFrame)
        assert list(obs.df.columns) == CSV_COLUMNS


def test_autosaveobserver_update_appends(monkeypatch, tmp_path):
    """Appends new row to DataFrame and saves CSV when auto-save enabled"""
    monkeypatch.setattr("app.observers.CALCULATOR_AUTO_SAVE", True)
    log_file = str(tmp_path / "auto.csv")
    obs = AutosaveObserver(log_file=log_file)

    message = {c: f"val_{c}" for c in CSV_COLUMNS}
    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        obs.update(message)
        mock_to_csv.assert_called_once()
        assert len(obs.df) == 1
        assert all(col in obs.df.columns for col in CSV_COLUMNS)


def test_autosaveobserver_update_no_autosave(monkeypatch, tmp_path):
    """Appends but does not save if CALCULATOR_AUTO_SAVE = False"""
    monkeypatch.setattr("app.observers.CALCULATOR_AUTO_SAVE", False)
    log_file = str(tmp_path / "auto.csv")
    obs = AutosaveObserver(log_file=log_file)

    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        msg = {c: "1" for c in CSV_COLUMNS}
        obs.update(msg)
        mock_to_csv.assert_not_called()
        assert len(obs.df) == 1


def test_autosaveobserver_update_write_error(monkeypatch, tmp_path):
    """Ensure exception in write logs error"""
    monkeypatch.setattr("app.observers.CALCULATOR_AUTO_SAVE", True)
    log_file = str(tmp_path / "auto.csv")
    obs = AutosaveObserver(log_file=log_file)

    with patch("pandas.DataFrame.to_csv", side_effect=Exception("disk fail")), \
         patch.object(logger, "error") as mock_err:
        obs.update({c: "x" for c in CSV_COLUMNS})
        mock_err.assert_called_once()
        assert "failed to save" in mock_err.call_args[0][0]

def test_autosaveobserver_load_existing_file(tmp_path):
    log_file = tmp_path / "existing.csv"
    data = pd.DataFrame([{"timestamp":"t1","operation":"add","operand1":1,"operand2":2,"result":3,"instance_id":"id1"}])
    data.to_csv(log_file, index=False)

    with patch("app.observers.logger") as mock_logger:
        obs = AutosaveObserver(log_file=str(log_file))
        pd.testing.assert_frame_equal(obs.df, data)
        mock_logger.info.assert_called_with(f"✅ AutosaveObserver loaded existing file: {obs.log_file}")

def test_autosaveobserver_init_exception(monkeypatch):
    """Simulate a failure during initialization"""
    # Force pd.read_csv to throw an exception
    monkeypatch.setattr("pandas.read_csv", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("read fail")))

    with patch("app.observers.logger") as mock_logger:
        with pytest.raises(FileAccessError) as excinfo:
            AutosaveObserver(log_file="dummy.csv")

        # Check that logger.error was called
        mock_logger.error.assert_called_once()
        assert "Failed to initialize AutosaveObserver" in mock_logger.error.call_args[0][0]

        # Check that exception message includes original error
        assert "read fail" in str(excinfo.value)

def test_autosaveobserver_update_empty_message(tmp_path):
    """Passing empty message logs a warning and does not alter df"""
    log_file = tmp_path / "auto.csv"
    obs = AutosaveObserver(log_file=str(log_file))
    
    # Patch logger to capture warnings
    with patch.object(logger, "warning") as mock_warn:
        obs.update(None)
        mock_warn.assert_called_once_with("❌ No data to save in AutosaveObserver.")
    
    # DataFrame should still be empty
    assert obs.df.empty

def test_autosaveobserver_update_exception(tmp_path):
    """Simulate an unexpected error during update"""
    log_file = tmp_path / "auto.csv"
    obs = AutosaveObserver(log_file=str(log_file))
    
    # Patch pd.concat to raise an exception
    with patch("pandas.concat", side_effect=Exception("concat fail")), \
         patch("app.observers.logger") as mock_logger:
        
        with pytest.raises(FileAccessError) as excinfo:
            obs.update({"timestamp": "t1", "operation": "add", "operand1": 1, "operand2": 2, "result": 3, "instance_id": "id1"})
        
        # Check that logger.error was called
        mock_logger.error.assert_called_once()
        assert "Error updating AutosaveObserver" in mock_logger.error.call_args[0][0]
        
        # Check that FileAccessError includes the original exception
        assert "concat fail" in str(excinfo.value)

# ----------------------------
# Subject Tests
# ----------------------------
def test_subject_notify_calls_observers(monkeypatch):
    subj = Subject()
    mock_observer = MagicMock()
    subj.attach(mock_observer)

    msg = ",".join(["v1", "v2", "v3", "v4", "v5", "v6"])
    subj.notify(msg)
    mock_observer.update.assert_called_once()
    call_arg = mock_observer.update.call_args[0][0]
    assert isinstance(call_arg, dict)
    assert set(call_arg.keys()) == set(CSV_COLUMNS)


def test_subject_notify_bad_column_count(monkeypatch):
    subj = Subject()
    with patch.object(logger, "error") as mock_err:
        subj.notify("too,few,columns")
        mock_err.assert_called_once()
        assert "Mismatch in expected columns" in mock_err.call_args[0][0]


def test_subject_notify_multiple_observers():
    subj = Subject()
    o1, o2 = MagicMock(), MagicMock()
    subj.attach(o1)
    subj.attach(o2)
    msg = ",".join(["a", "b", "c", "d", "e", "f"])
    subj.notify(msg)
    o1.update.assert_called_once()
    o2.update.assert_called_once()