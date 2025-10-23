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
        prompt = (
                f"{Fore.RED}⚠️ Are you sure you want to delete the calculator history? "
                f"All memory will be lost!{Style.RESET_ALL} "
                f"{Fore.RED}Y{Style.RESET_ALL}/{Fore.RED}N{Style.RESET_ALL}: "
            )

        user_input = input(prompt).strip().upper()

        if user_input =="Y" or user_input=="YES":

            # Delete CSV file
            self.caretaker.delete_saved_history(self.originator)
            logger.info("✅ User confirmed and deleted both in-memory and saved history.")

        elif user_input =="N" or user_input=="NO":
            print(f"✅ History deletion aborted by user")
            logger.info("✅ User aborted history deletion request")




    # ----------------- Observers -----------------
    def notify_observers(self, final_message: str):
        self.subject.notify(final_message)


    def load_history(self):
        if len(self.originator.history) >0:
            logger.warning("❌ User attempted to override existing history, operation aborted")
            raise CommandError("❌ existing history cannot be overridden; can load previous history only if no current history exists")
        else:
            self.caretaker.get_loaded_history(self.originator)

    def save_history(self):
        self.caretaker.save_history_to_csv(self.originator)

    def clear_history(self):
        self.originator.delete_history()
        logger.warning("✅ Instance history cleared")


