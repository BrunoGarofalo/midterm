# app/calculator_config.py
import os
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables from .env
load_dotenv()

# helper function for safely reading and converting environment variables
def get_env(name, default=None, cast=None): # pragma: no cover
    value = os.getenv(name, default) 
    if cast: 
        if cast == bool:
            value = str(value).lower() in ("1", "true", "yes", "on")
        else:
            try:
                value = cast(value)
            except Exception as e:
                raise ValueError(f"Invalid value for {name}: {value}") from e
    return value

# Base Directories
CALCULATOR_LOG_DIR = os.getenv("CALCULATOR_LOG_DIR", "logs")
CALCULATOR_HISTORY_DIR = os.getenv("CALCULATOR_HISTORY_DIR", "history")

# Files
CSV_HISTORY_FILE = os.getenv("CSV_HISTORY_FILE", "history_log.csv")
LOG_HISTORY_FILE = os.getenv("LOG_HISTORY_FILE", "event_log.txt")
TXT_HISTORY_FILE = os.getenv("TXT_HISTORY_FILE", "history_log.json")
CSV_CARETAKER_HISTORY_FILE = os.getenv("CSV_CARETAKER_HISTORY_FILE", "caretaker_history.csv")  # memento source of truth

# File columns
DEFAULT_COLUMNS = ["timestamp", "operation", "operand1", "operand2", "result", "instance_id"]
CSV_COLUMNS = os.getenv("CSV_COLUMNS")
if CSV_COLUMNS: 
    CSV_COLUMNS = [c.strip() for c in CSV_COLUMNS.split(",")]
else:
    CSV_COLUMNS = DEFAULT_COLUMNS # pragma: no cover

# History Settings
CALCULATOR_MAX_HISTORY_SIZE = int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "100"))
CALCULATOR_AUTO_SAVE = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower() == "true"

# Calculation Settings
CALCULATOR_PRECISION = int(os.getenv("CALCULATOR_PRECISION", "4"))
CALCULATOR_MAX_INPUT_VALUE = Decimal(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1000"))
CALCULATOR_DEFAULT_ENCODING = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")
