import logging
import os
from dotenv import load_dotenv
load_dotenv()

# Optional: configuration
LOG_DIR = os.getenv("CALCULATOR_LOG_DIR", ".")
LOG_FILE = os.getenv("LOG_HISTORY_FILE", ".")
LOG_FILE = os.path.join(LOG_DIR, LOG_FILE)

os.makedirs(LOG_DIR, exist_ok=True)

# Configure the logger
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
