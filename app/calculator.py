from app.command_factory import CommandFactory
from decimal import Decimal, InvalidOperation
from app.observers import LoggingObserver, Subject, AutosaveObserver
from datetime import datetime
from app.memento import Originator, CareTaker
from app.logger import logger
from app.exceptions import OperationError, ValidationError, CommandError, HistoryError
from colorama import init, Fore, Style
from app.logger import logger
from dotenv import load_dotenv
import os
import uuid
import pandas as pd
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

''''
who should delete the history? the logging observer or the originator in the memento?
Should the history be cleared when the instance ends? both the instance history and in the txt file?
Should the redone operation be recalculated? meaning the operands should be re entered?
should the logging observer save the history only when prompted?
Manual save is supposed to save to a CSV? would that override the history saved by the autosave observer?
'''

class Calculator:

    # define operations
    operations_dictionary = {'A':['Percentage', 'Percentage'], 
                        'B': ['Modulo', 'Modulo'], 
                        'C': ['Multiplication', 'Multiplication'], 
                        'D': ['Root', 'Root'],
                        'E': ['Absolute Difference', 'AbsDiff'],
                        'F': ['Integer Division', 'IntDiff'],
                        'G': ['Addition', 'add'],
                        'H': ['Subtraction', 'subtract'],
                        'I': ['Division', 'div'],
                        'J': ['Power', 'power'],
                        'K': ['Display history', 'hist'],
                        'L': ['Clear history', 'clear'],
                        'M': ['Undo previous operations', 'undo'],
                        'N': ['Redo current operation', 'redo'],
                        'O': ['Save calculation history', 'save'],
                        'P': ['Load calculation history', 'load'],
                        'Q': ['Exit the program', 'exit']}
        
    def __init__(self):
        self.originator = Originator()
        self.caretaker = CareTaker()
        self.subject = Subject()
        self.instance_ID =  str(uuid.uuid4())

        # Attach observers
        self.logging_observer = LoggingObserver()
        self.autosave_observer = AutosaveObserver()

        self.subject.attach(self.logging_observer )
        self.subject.attach(self.autosave_observer)



        
        
    @classmethod
    def show_commands(cls):
        """Return a formatted string of all available commands."""
        return "\n".join([f"{key:<2}: {value[0]}" for key, value in cls.operations_dictionary.items()])

    @classmethod
    def get_operation_code(cls, user_input: str):
        """Return the operation code (short name) for a given input letter."""
        if user_input in cls.operations_dictionary:
            op_code = cls.operations_dictionary[user_input][1]
            logger.info(f"✅ Determined operation code '{op_code}' for command '{user_input}'")
            return op_code
        else:
            logger.warning(f"❌ Invalid operation key: {user_input}")
            raise CommandError(f"❌Calculator.py#1 - Invalid command '{user_input}'. Type 'help' to see available commands.")
    
     # ----------------- Operations -----------------
    def create_operation(self, op_code: str):
        """
        Creates an operation object from the operation code.
        """
        try:
            return CommandFactory(op_code).createOperationObject()
        except Exception as e:
            raise OperationError(f"❌ Calculator.py#2 -  Failed to create operation: {e}")

    # ----------------- History / Undo / Redo -----------------
    def add_operation(self, message: str):
        self.caretaker.save_memento(self.originator.create_memento())
        self.originator.add_operation(message)
        self.notify_observers(message)

    def undo(self):
        logger.info("Undo requested by user")
        return self.caretaker.undo_memento(self.originator)


    def redo(self):
        logger.info("Redo requested by user")
        return self.caretaker.redo_memento(self.originator)

    def show_history(self):
        if not self.originator.history:
            print(f"⚠️ {Fore.YELLOW} No history available.{Style.RESET_ALL}")
            logger.warning("Attempted to display history but it is empty")
            # return "No history available"

        for op in self.originator.history:
            print(op)

        logger.info("✅ History displayed")

    def delete_history(self):
        self.originator.history.clear()

        # Optionally clear observers as well
        self.logging_observer.delete_history()
        # self.autosave_observer.delete_history()

    # ----------------- Observers -----------------
    def notify_observers(self, final_message: str):
        self.subject.notify(final_message)


    def save_history(self):
        self.logging_observer.save_history(self.originator.history)
        logger.info("✅ History saved manually to history_log.txt")

    def load_history(self):
        loaded = self.autosave_observer.load_history()
        self.originator.get_loaded_history(loaded)
        self.caretaker.save_memento(self.originator.create_memento())
        logger.info("✅ App history loaded from history_log.csv")

    def clear_history(self):
        self.originator.delete_history()
        logger.warning("✅ Instance history cleared")

#---------------------clear or load history ----------------------
def delete_history(self):
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


def load_history(self):
    try:
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            logger.warning("❌ AutosaveObserver attempted to load history but folder is missing/empty")
            print(f"❌ {Fore.MAGENTA} No saved history to load{Style.RESET_ALL}")
            return []
        
        df = pd.read_csv(self.log_file, encoding=CALCULATOR_DEFAULT_ENCODING)
        if df.empty:
            logger.warning("❌ AutosaveObserver attempted to load history but file is empty")
            print(f"❌{Fore.MAGENTA} History file is empty{Style.RESET_ALL}")
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