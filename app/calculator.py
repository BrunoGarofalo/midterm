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

class Calculator:

    # define operations library
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
    
    # --------------------- CLASS CONSTRUCTOR ---------------------------
    def __init__(self):

        # initialize originator
        self.originator = Originator()

        # initialize caretaker
        self.caretaker = CareTaker()

        # initialize subject
        self.subject = Subject()

        #get instance ID
        self.instance_ID =  str(uuid.uuid4())

        # initialzie observers
        self.logging_observer = LoggingObserver()
        self.autosave_observer = AutosaveObserver()

        # Attach observers
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
    
     # ----------------- Create operation object -----------------
    def create_operation(self, op_code: str):
        """
        Creates an operation object from the operation code.
        """
        try:
            return CommandFactory(op_code).createOperationObject()
        except Exception as e:
            raise OperationError(f"❌ Calculator.py#2 -  Failed to create operation: {e}")

    # ----------------- History / Undo / Redo -----------------

    # Add new operation to history stack
    def add_operation(self, message: str):
        self.caretaker.save_memento(self.originator.create_memento())
        self.originator.add_operation(message)

    # perform undo
    def undo(self):
        logger.info("⚠️ Undo requested by user")
        return self.caretaker.undo_memento(self.originator)

    # perform redo
    def redo(self):
        logger.info("⚠️ Redo requested by user")
        return self.caretaker.redo_memento(self.originator)

    # show history
    def show_history(self):
        if not self.originator.history:
            print(f"⚠️ {Fore.YELLOW} No history available.{Style.RESET_ALL}")
            logger.warning("Attempted to display history but it is empty")

        for op in self.originator.history:
            print(op)

        logger.info("✅ History displayed")

    # delete all history
    def delete_history(self):
        '''
        History should not be delete but I'm giving the user the option to do it only after validating the choice
        '''

        while True:

            prompt = (
                    f"{Fore.RED}⚠️ Are you sure you want to delete the calculator history? "
                    f"All memory will be lost!{Style.RESET_ALL} "
                    f"{Fore.RED}Y{Style.RESET_ALL}/{Fore.RED}N{Style.RESET_ALL}: "
                )
            try:
                # get user input
                user_input = input(prompt).strip().upper()

            except EOFError:
                logger.warning("❌ No input received; aborting history deletion")
                return
            
            # Ask user to confirm action
            if user_input in ("Y", "YES"):

                # Delete history
                self.caretaker.delete_saved_history(self.originator)
                logger.info("✅ User confirmed and deleted both in-memory and saved history.")
                break

                # else abort operation
            elif user_input in ("N", "NO"):
                print(f"✅ History deletion aborted by user")
                logger.info("✅ User aborted history deletion request")
                break
            else:
                # handle wrong command
                print(f"⚠️ {Fore.YELLOW} Please enter either Y or N")
                logger.info(f"❌ User entered wrong input {user_input} for data delete request")
                




    # ----------------- Observers -----------------

    # method to notify observers of new calculation
    def notify_observers(self, final_message: str): # pragma: no cover
        self.subject.notify(final_message)

    # method to load history from CSV
    def load_history(self): # pragma: no cover
        if len(self.originator.history) >0:
            logger.warning("❌ User attempted to override existing history, operation aborted")
            raise CommandError("❌ existing history cannot be overridden; can load previous history only if no current history exists")
        else:
            self.caretaker.get_loaded_history(self.originator)

    # method to save the history to the CSV
    def save_history(self):
        self.caretaker.save_history_to_csv(self.originator)



