import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
from app.observers import LoggingObserver, AutosaveObserver, Subject
from app.exceptions import FileAccessError, HistoryError, DataFormatError
from app.config import CALCULATOR_MAX_HISTORY_SIZE, CALCULATOR_AUTO_SAVE, CALCULATOR_DEFAULT_ENCODING, CALCULATOR_DEFAULT_ENCODING
from app.logger import logger

# ----------------------------
# LoggingObserver Tests
# ----------------------------
def test_loggingobserver_init_exception(monkeypatch):
    # Simulate os.makedirs failure
    monkeypatch.setattr(os, "makedirs", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("dir fail")))
    
    with pytest.raises(FileAccessError) as excinfo:
        LoggingObserver()
    assert "Failed to create log directory" in str(excinfo.value)


def test_loggingobserver_save_history_empty(monkeypatch):
    # Initialize observer
    observer = LoggingObserver()

    # Patch logger to capture warnings
    with patch.object(logger, "warning") as mock_warning:
        # Pass empty string (or None) instead of list
        observer.save_calculation("")  # empty message

        # Assert logger.warning was called
        mock_warning.assert_called_once_with("❌ Attempted to save empty history. No data written.")
    

def test_loggingobserver_save_calculation_file_error(monkeypatch):
    observer = LoggingObserver()

    # Patch open to raise an IOError when trying to write
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: (_ for _ in ()).throw(IOError("file fail")))

    with pytest.raises(FileAccessError):
        observer.save_calculation("5 + 2 = 7")



# ----------------------------
# AutosaveObserver Tests
# ----------------------------
def test_autosaveobserver_init_file_error(monkeypatch):
    # Simulate os.makedirs success
    monkeypatch.setattr(os, "makedirs", lambda *args, **kwargs: None)
    
    # Simulate pd.read_csv failure
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("read fail")))
    
    with pytest.raises(FileAccessError):
        AutosaveObserver(log_file="dummy.csv")


def test_autosaveobserver_update_exception(monkeypatch):
    observer = AutosaveObserver()
    
    # Patch pandas concat to raise
    monkeypatch.setattr(pd, "concat", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("concat fail")))
    
    with pytest.raises(FileAccessError):
        observer.save_calculation("2025-10-20|add|5|2|7")


def test_autosaveobserver_delete_history_exception():
    observer = AutosaveObserver()

    # Patch the to_csv method on pandas.DataFrame to force an exception
    with patch("pandas.DataFrame.to_csv", side_effect=Exception("disk write error")):
        with pytest.raises(FileAccessError) as excinfo:
            observer.delete_history()

    assert "Error clearing autosave history" in str(excinfo.value)


def test_autosaveobserver_load_history_file_not_found(monkeypatch):
    observer = AutosaveObserver()
    
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    
    result = observer.load_history()
    assert result == []


def test_autosaveobserver_load_history_empty_file(monkeypatch):
    observer = AutosaveObserver()
    
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: pd.DataFrame())
    
    result = observer.load_history()
    assert result == []


def test_autosaveobserver_load_history_empty_data(monkeypatch):
    observer = AutosaveObserver()
    
    # Simulate empty CSV raising EmptyDataError
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: (_ for _ in ()).throw(pd.errors.EmptyDataError()))
    
    with pytest.raises(DataFormatError):
        observer.load_history()


def test_autosaveobserver_load_history_file_error(monkeypatch):
    observer = AutosaveObserver()
    
    # Simulate generic exception in load
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("load fail")))
    
    with pytest.raises(FileAccessError):
        observer.load_history()


# ----------------------------
# Subject Tests
# ----------------------------
def test_subject_notify_exception(monkeypatch):
    subj = Subject()
    
    # Create fake observer whose update raises
    class BadObserver:
        def update(self, msg):
            raise Exception("update fail")
    
    subj.attach(BadObserver())
    
    with pytest.raises(Exception):
        subj.notify("test message")

# ------------------------------------------------------------------------
# TEST: Saving an empty message should log a warning and print a message
# ------------------------------------------------------------------------
def test_save_calculation_empty_message(caplog):
    observer = LoggingObserver()
    
    with patch("builtins.print") as mock_print:
        observer.save_calculation("")

    assert "Attempted to save empty history" in caplog.text
    mock_print.assert_called_once()
    # Ensure method exits without raising
    assert not any("Error" in rec.message for rec in caplog.records)


# ------------------------------------------------------------------------
# TEST: Successful save should write to file and log success
# ------------------------------------------------------------------------
def test_save_calculation_success(tmp_path, caplog):
    log_file = tmp_path / "test_log.txt"

    with patch("os.path.join", return_value=str(log_file)):
        observer = LoggingObserver()

    message = "2025-10-21|add|2|3|5"
    with patch("builtins.open", mock_open()) as mocked_file:
        observer.save_calculation(message)

    mocked_file.assert_called_once_with(observer.log_file, "a", encoding=CALCULATOR_DEFAULT_ENCODING)
    handle = mocked_file()
    handle.write.assert_called_once_with(message + "\n")

    assert "✅ New calculation saved" in caplog.text


# ------------------------------------------------------------------------
# TEST: Failing to save (e.g., file write error) raises FileAccessError
# ------------------------------------------------------------------------
def test_save_calculation_write_error(tmp_path):
    log_file = tmp_path / "bad_log.txt"

    with patch("os.path.join", return_value=str(log_file)):
        observer = LoggingObserver()

    message = "2025-10-21|divide|10|2|5"

    # Patch open to raise an Exception and patch correct logger path
    with patch("builtins.open", side_effect=Exception("disk error")), \
         patch("app.observers.logger") as mock_logger:
        with pytest.raises(FileAccessError):
            observer.save_calculation(message)

def test_delete_history_success(tmp_path):
    # Create a dummy log file
    log_file = tmp_path / "history.txt"
    log_file.write_text("dummy content")

    with patch("os.path.join", return_value=str(log_file)):
        observer = LoggingObserver()
        # Should delete without errors
        observer.delete_history()
        assert not log_file.exists()


def test_delete_history_file_not_found(tmp_path):
    log_file = tmp_path / "nonexistent.txt"

    with patch("os.path.join", return_value=str(log_file)):
        observer = LoggingObserver()
        with pytest.raises(OSError) as exc_info:  # <- changed from FileNotFoundError
            observer.delete_history()
        assert "File not found" in str(exc_info.value)


def test_delete_history_permission_error(tmp_path):
    # Create a file but simulate PermissionError
    log_file = tmp_path / "protected.txt"
    log_file.write_text("dummy content")

    with patch("os.path.join", return_value=str(log_file)):
        observer = LoggingObserver()
        with patch("os.remove", side_effect=PermissionError("no permission")):
            with pytest.raises(PermissionError) as exc_info:
                observer.delete_history()
            assert "Permission denied" in str(exc_info.value)

def test_autosaveobserver_trim_and_save(tmp_path, monkeypatch):
    # Patch the value in the observers module, where it is actually used
    monkeypatch.setattr("app.observers.CALCULATOR_MAX_HISTORY_SIZE", 3)

    log_file = str(tmp_path / "autosave.csv")
    observer = AutosaveObserver(log_file=log_file)

    for i in range(5):
        msg = f"2025-10-21|add|{i}|{i}|{i+i}"
        observer.save_calculation(msg)

    # Trim applied correctly
    assert len(observer.df) == 3
    assert observer.df.iloc[0]["operand1"] == "2"  # oldest row kept
