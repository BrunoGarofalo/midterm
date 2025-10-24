import logging
import os
from dotenv import load_dotenv

load_dotenv()

# file paths
LOG_DIR = os.getenv("CALCULATOR_LOG_DIR", ".")
LOG_FILE = os.getenv("LOG_HISTORY_FILE", "history.log")
LOG_FILE = os.path.join(LOG_DIR, LOG_FILE)

os.makedirs(LOG_DIR, exist_ok=True)

# Create a single logger
logger = logging.getLogger("calculator")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if imported multiple times
if not logger.hasHandlers():
    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)