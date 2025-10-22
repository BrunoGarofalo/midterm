import logging
import os
from unittest.mock import patch, MagicMock
# import builtins
# import pytest
import importlib

# Import your logger module
import app.logger as logger_module


# ----------------------------
# Test directory creation
# ----------------------------
def test_log_dir_created(tmp_path):
    """Ensure LOG_DIR is created if it doesn't exist."""
    test_dir = tmp_path / "logs"
    with patch("os.makedirs") as makedirs_mock:
        with patch.dict("os.environ", {"CALCULATOR_LOG_DIR": str(test_dir)}):
            # reload the logger module to trigger directory creation
            import importlib
            importlib.reload(logger_module)
            makedirs_mock.assert_called_once_with(str(test_dir), exist_ok=True)


# ----------------------------
# Test logger has FileHandler
# ----------------------------
def test_logger_file_handler_exists():
    """Logger should have at least one FileHandler."""
    import os

    with patch.dict("os.environ", {"CALCULATOR_LOG_DIR": ".", "LOG_HISTORY_FILE": "test_history.log"}):
        import app.logger as logger_module

        # Patch hasHandlers to always return False so FileHandler is added
        with patch.object(logger_module.logger, "hasHandlers", return_value=False):
            importlib.reload(logger_module)

        logger = logger_module.logger
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0, "Logger should have a FileHandler attached"


