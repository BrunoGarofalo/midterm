
import os
import pandas as pd
from decimal import Decimal
from app.logger import logger
from app.config import (
    CALCULATOR_MAX_HISTORY_SIZE, 
    CALCULATOR_AUTO_SAVE, 
    CALCULATOR_DEFAULT_ENCODING,
    CALCULATOR_HISTORY_DIR,
    CSV_HISTORY_FILE,
    TXT_HISTORY_FILE
)

from app.exceptions import FileAccessError, DataFormatError, HistoryError
from colorama import init, Fore, Style
init(autoreset=True) 


# ------------------------------------------------------------
# LoggingObserver
# ------------------------------------------------------------
class LoggingObserver:
    def __init__(self, log_file=TXT_HISTORY_FILE):
        try:

            # Ensure the history directory exists
            os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)
            self.log_file = os.path.join(CALCULATOR_HISTORY_DIR, log_file)
            logger.info(f"✅ LoggingObserver initialized with log file: {self.log_file}")
            # self.history = []
        
        except Exception as e:
            logger.exception("❌ Failed to initialize LoggingObserver  {e}")
            raise FileAccessError(f"❌ Failed to create log directory: {e}")

    # method that appends new calculation to TXT file
    def save_calculation(self, message):
        if not message:
            logger.warning("❌ Attempted to save empty history. No data written.")
            print(f"❌{Fore.MAGENTA} No history to be saved.{Style.RESET_ALL}")
            return
        
        try:
            with open(self.log_file, "a",encoding=CALCULATOR_DEFAULT_ENCODING) as file:
                file.write(message + "\n")
            logger.info(f"✅ New calculation saved to {self.log_file}")
            # print(f"✅ {Fore.GREEN} Full history successfully saved to history_log.txt{Style.RESET_ALL}")
        except Exception as e:
            logger.warning("❌ Failed to save new calculation {e}")
            raise FileAccessError(f"Error saving calculation {message} to file: {e}")

    def delete_history(self):
        #Delete the history file safely
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
                print(f"✅ Deleted {self.log_file}")
            else:
                raise FileNotFoundError(f"⚠️ File not found: {self.log_file}")
        except PermissionError as e:
            raise PermissionError(f"❌ Permission denied: cannot delete {self.log_file}") from e
        except OSError as e:
            raise OSError(f"❌ Error deleting file {self.log_file}: {e}") from e

    # def detach(self, final_message):
    #     try:
    #         if hasattr(self, "history") and final_message in self.history:
    #             self.history.remove(final_message)
    #             logger.info(f"LoggingObserver detached operation: {final_message}")
    #     except Exception as e:
    #         logger.exception("❌ Failed to detach operation from LoggingObserver.")
    #         raise HistoryError(f"❌ Error detaching operation: {e}")


# ------------------------------------------------------------
# AutosaveObserver
# ------------------------------------------------------------
class AutosaveObserver:

    def __init__(self, log_file=CSV_HISTORY_FILE):
        try:
            # Ensure the history directory exists
            os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)

            self.log_file = os.path.join(CALCULATOR_HISTORY_DIR, log_file)
            self.columns = ["timestamp", "operation", "operand1", "operand2", "result"]

            # If the file doesn't exist or is empty, create a new one
            if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
                self.df = pd.DataFrame(columns=self.columns)
                self.df.to_csv(self.log_file, index=False)
                logger.info(f"✅ AutosaveObserver initialized new file: {self.log_file}")
            else:
                self.df = pd.read_csv(self.log_file)
                logger.info(f"✅ AutosaveObserver loaded existing file: {self.log_file}")
        
        except Exception as e:
            logger.exception("❌ Failed to initialize AutosaveObserver.")
            raise FileAccessError(f"❌ Error initializing AutosaveObserver: {e}")

    #method that adds the new calculation log to 
    def save_calculation(self, final_message):
        try:
            #get individual values from message
            message_values = final_message.split("|")

            #zip values to create key-value pairs and create dict
            values_dict = dict(zip(self.columns, message_values))

            #create new data row in pandas
            new_row = pd.DataFrame([values_dict])

            #add new row to df
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            # Trim to max history size
            if len(self.df) > CALCULATOR_MAX_HISTORY_SIZE:
                self.df = self.df.tail(CALCULATOR_MAX_HISTORY_SIZE)

            # Only save automatically if enabled
            if CALCULATOR_AUTO_SAVE:
                self.df.to_csv(self.log_file, index=False, encoding=CALCULATOR_DEFAULT_ENCODING)
                logger.info(f"✅ AutosaveObserver auto-saved operation: {final_message}")

            logger.info(f"✅ AutosaveObserver updated with operation: {final_message}")
        
        except DataFormatError:
            raise
        except Exception as e:
            logger.exception("❌ Error updating AutosaveObserver {e}")
            raise FileAccessError(f"❌ Error updating autosave file: {e}")

    
    def delete_history(self):
        try:
            self.df = pd.DataFrame(columns=self.columns)  
            self.df.to_csv(self.log_file, index=False)   

            logger.warning(f"✅ AutosaveObserver cleared history in {self.log_file}")
        
        except Exception as e:
            logger.exception("❌ Failed to clear autosave history.")
            raise FileAccessError(f"❌ Error clearing autosave history: {e}")

    
    def load_history(self):
        try:
            if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
                logger.warning("❌ AutosaveObserver attempted to load history but folder is missing/empty")
                print(f"❌ {Fore.MAGENTA} No saved history to load{Style.RESET_ALL}")
                return []
            
            df = pd.read_csv(self.log_file, encoding=CALCULATOR_DEFAULT_ENCODING)
            if df.empty:
                logger.warning("❌ AutosaveObserver attempted to load history but file is empty")
                print(f"❌{Fore.Magenta} History file is empty{Style.RESET_ALL}")
                return []

            loaded_calculations = []

            for _, row in df.iterrows():
                operation_record = f"{row["timestamp"]}|{row["operation"]}|{row["operand1"]}|{row["operand2"]}|{row["result"]}"
                loaded_calculations.append(operation_record)

            logger.info(f"✅ AutosaveObserver loaded {len(loaded_calculations)} history entries from {self.log_file}")
            return loaded_calculations
        
        except pd.errors.EmptyDataError:
            logger.warning("❌ AutosaveObserver encountered an empty CSV file.")
            raise DataFormatError("❌ CSV file is empty or corrupt.")
        
        except FileNotFoundError:
            logger.error(f"❌ History file not found: {self.log_file}")
            raise FileAccessError("❌ History file not found.")
        
        except Exception as e:
            logger.exception("❌ Error loading history file.")
            raise FileAccessError(f"❌ Error loading history file: {e}")

# ------------------------------------------------------------
# Subject
# ------------------------------------------------------------
class Subject:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, final_message):
        for observer in self.observers:
            observer.save_calculation(final_message)
