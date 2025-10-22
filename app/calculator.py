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
