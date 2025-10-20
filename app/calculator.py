from app.operation_selection import operationSelection
from app.command_factory import CommandFactory
from decimal import Decimal, InvalidOperation
from app.observers import LoggingObserver, Subject, AutosaveObserver
from datetime import datetime
from app.memento import Originator, CareTaker
from app.logger import logger
from app.input_validators import get_valid_operand
from app.exceptions import OperationError, ValidationError, CommandError, HistoryError
from colorama import init, Fore, Style
import logging
import os
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
    def __init__(self):
        self.originator = Originator()
        self.caretaker = CareTaker()
        self.subject_logging = Subject()
        self.subject_autosave = Subject()

        # Logging info
        self.log_dir = os.getenv("CALCULATOR_LOG_DIR", ".")
        self.log_file = os.getenv("LOG_HISTORY_FILE", "history.log")
        self.log_file = os.path.join(self.log_dir, self.log_file)

        #initialize logger
        self.initialize_logger()

        # Attach observers
        self.logging_observer = LoggingObserver()
        self.autosave_observer = AutosaveObserver()
        self.subject_logging.attach(self.logging_observer)
        self.subject_autosave.attach(self.autosave_observer)

        self.operations_dictionary = {'A':['Percentage', 'Percentage'], 
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
        
    def initialize_logger(self):
        # Ensure directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Configure the logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # Prevent adding multiple handlers if multiple instances
        if not self.logger.hasHandlers():
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.info("Calculator initialized")

    def log(self, message: str, level="info"):
        """Convenience method to log messages."""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.debug(message)
        
    @classmethod
    def show_commands(cls):
        """Return a formatted string of all available commands."""
        return "\n".join([f"{key:<2}: {value[0]}" for key, value in cls.operations_dictionary.items()])

    @classmethod
    def get_operation_code(cls, user_input: str):
        """Return the operation code (short name) for a given input letter."""
        if user_input in cls.operations_dictionary:
            op_code = cls.operations_dictionary[user_input][1]
            cls.log(f"Determined operation code '{op_code}' for command '{user_input}'", "info")
            return op_code
        else:
            cls.log(f"❌ Invalid operation key: {user_input}", "warning")
            raise CommandError(f"❌ Invalid command '{user_input}'. Type 'help' to see available commands.")
    
    #--------------------Validate operand -----------------
    def get_validated_operand(prompt: str, operation_obj=None, operand_a: Decimal | None = None) -> Decimal:
        """
        Prompt for an operand until valid.
        If operation_obj has a check_decimals method, validate the input.
        For the second operand, pass operand_a for validation if needed.
        """
        while True:
            operand = get_valid_operand(prompt)
            try:
                if operation_obj and hasattr(operation_obj, "check_decimals"):
                    if operand_a is None:
                        # first operand
                        operation_obj.check_decimals(operand, Decimal("1"))
                    else:
                        # second operand
                        operation_obj.check_decimals(operand_a, operand)
                break
            except (ValueError, ValidationError) as e:
                print(f"{Fore.RED}{e}. Please re-enter.{Style.RESET_ALL}")
                # self.log(f"Invalid operand entered: {operand}, Error: {e}", "error")
        return operand

     # ----------------- Operations -----------------
    def create_operation(self, op_code: str):
        """
        Creates an operation object from the operation code.
        """
        try:
            return CommandFactory(op_code).createOperationObject()
        except Exception as e:
            raise OperationError(f"Failed to create operation: {e}")

    # ----------------- History / Undo / Redo -----------------
    def add_operation(self, message: str):
        self.caretaker.save_memento(self.originator.create_memento())
        self.originator.add_operation(message)
        self.notify_observers(message)

    def undo(self):
        self.log("Undo requested by user", "info")
        return self.caretaker.undo_memento(self.originator)


    def redo(self):
        self.log("Redo requested by user", "info")
        return self.caretaker.redo_memento(self.originator)

    def show_history(self):
        for op in self.originator.history:
            print(op)
        self.log("History displayed", "info")

    def delete_history(self):
        self.originator.history.clear()
        # Optionally clear observers as well
        self.logging_observer.history.clear()
        self.autosave_observer.delete_history()

    # ----------------- Observers -----------------
    def notify_observers(self, final_message: str):
        self.subject_logging.notify(final_message)
        self.subject_autosave.notify(final_message)

    def save_history(self):
        self.logging_observer.save_history(self.originator.history)
        self.log("History saved manually to history_log.txt", "info")

    def load_history(self):
        loaded = self.autosave_observer.load_history()
        self.originator.get_loaded_history(loaded)
        self.caretaker.save_memento(self.originator.create_memento())
        self.log("App history loaded from history_log.csv", "info")

    def clear_history(self):
        self.originator.delete_history()
        self.log("Instance history cleared", "warning")
        ##################################

    # ----------------- Commands -----------------
    def show_commands(self):
        from app.operation_selection import operationSelection
        self.log("Command list displayed", "info")
        return operationSelection.show_commands()

    def get_operation_code(self, user_input: str):
        from app.operation_selection import operationSelection
        self.log("COperation selection requested", "info")
        return operationSelection.get_operation_code(user_input)


#################################################################################################################################
# def main():
#     logger.info("Calculator application started")

#     caretaker = CareTaker()
#     originator = Originator()

#     #instantiate and attach observers
#     logging_observer = LoggingObserver()
#     autosave_observer = AutosaveObserver()

#     '''
#     I need to simplify, I do not want 2 subjects
#     simplify by having originator.attach_observer() and originator internally calls notify whenever add_operation is called
#     '''
#     subject_logging = Subject()
#     subject_autosave = Subject()

#     subject_logging.attach(logging_observer)
#     subject_autosave.attach(autosave_observer)

#     print(f"{Fore.CYAN}👋 Welcome to the Calculator app! Type 'help' to see available commands.{Style.RESET_ALL}")

#     while True:
#         try:

#             # Prompt user for operation
#             user_input = input(f"{Fore.MAGENTA}👉 Select one of the letters corresponding to the operation (IE: A for Percent: {Style.RESET_ALL}){Fore.YELLOW} - (Type 'help' to see available commands)").strip().upper()
#             print(user_input)

#             if user_input == "HELP":
#                 print("\n📜 Available commands, select one of the letters correspondint to the operation, IE: A for Percent:")
#                 print(operationSelection.show_commands())
#                 continue

#             if user_input not in operationSelection.operations_dictionary:
#                 raise CommandError(f"'{user_input}' not recognized. Type 'help' for the list.")

            

#             operation_code = operationSelection.operations_dictionary[user_input][1].lower()
#             logger.info(f"User selected operation: {operation_code}")

#             ################## EXIT #####################
#             if operation_code == "exit":
#                 originator.delete_history()
#                 logger.info("Application closed!")
#                 print("Goodbye!!")
#                 break
#             ################## SAVE #####################
#             if operation_code=='save':
#                 logging_observer.save_history(originator.history)
#                 logger.info("History saved manually to history_log.txt")
#                 continue

#             ################## HISTORY #####################
#             if operation_code == 'hist': 
#                 originator.show_history()
#                 logger.info("History displayed")
#                 continue
                
#             ################## CLEAR HISTORY #####################
#             if operation_code == 'clear':
#                 # autosave_observer.delete_history()
#                 originator.delete_history()
#                 logger.warning("Instance history cleared")
#                 continue

#             ################## UNDO #####################
#             if operation_code == 'undo':
#                 logger.info("Undo requested by user")

#                 undone_op = caretaker.undo_memento(originator)
#                 if undone_op:
#                     print(f"↩️ Undo performed: {undone_op}")
#                     for op in originator.history:
#                         subject_autosave.notify(op)
#                 continue

#             ################## REDO #####################
#             if operation_code == 'redo':
#                 logger.info("Redo requested by user")

#                 redone_op = caretaker.redo_memento(originator)
#                 if redone_op:
#                     print(f"↪️ Redo performed: {redone_op}")
#                     for op in originator.history:
#                         subject_autosave.notify(op)
#                 continue


#             ################## LOAD #####################
#             if operation_code == 'load':
#                 CSV_history = autosave_observer.load_history()
#                 originator.get_loaded_history(CSV_history)
#                 caretaker.save_memento(originator.create_memento()) 
#                 logger.info("App history loaded from history_log.csv")
#                 continue


#             try:
#                 operation_obj = CommandFactory(operation_code).createOperationObject()
#                 print(f"{Fore.YELLOW}Operation Selected: {operation_obj.__class__.__name__}{Style.RESET_ALL}")
#             except Exception as e:
#                 logger.error(f"Calculation error: {e}")
#                 raise OperationError(f"❌ Failed to create operation object: {e}")

#             ################## CALCULATIONS #####################
#             if hasattr(operation_obj, "calculate"):
#                 try:
#                     # === Get operand A with validation ===
#                     while True:
#                         operand_a = get_valid_operand("Enter first operand: ")

#                         try:
#                             if hasattr(operation_obj, "check_decimals"):
#                                 # Validate 'a' using the same method, passing b=1 as dummy if needed
#                                 operation_obj.check_decimals(operand_a, Decimal("1"))
#                             break  # Operand A is valid
#                         except (ValueError, ValidationError) as e:
#                             print(f"{Fore.RED} {e}. Please re-enter the first operand.{Style.RESET_ALL}")
#                             logger.warning(f"❌ Invalid first operand for {operation_obj.__class__.__name__}: {e}")

#                     # === Get operand B with validation ===
#                     while True:
#                         operand_b = get_valid_operand("Enter second operand: ")

#                         try:
#                             if hasattr(operation_obj, "check_decimals"):
#                                 operation_obj.check_decimals(operand_a, operand_b)
#                             break  # Operand B is valid
#                         except (ValueError, ValidationError) as e:
#                             print(f"{Fore.RED} {e}. Please re-enter the second operand.{Style.RESET_ALL}")
#                             logger.warning(f"❌ Invalid second operand for {operation_obj.__class__.__name__}: {e}")


#                     #Get results
#                     results = operation_obj.calculate(operand_a, operand_b)

#                     #logger message
#                     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                     final_message = f"{timestamp}|{operation_obj.__class__.__name__}|{operand_a}|{operand_b}|{results} "

#                     #create memento of current state (before change)
#                     caretaker.save_memento(originator.create_memento())

#                     #add the new operation (this changes the state)
#                     originator.add_operation(final_message)

#                     #notify observers
#                     subject_autosave.notify(final_message)

#                     #Log  successful completion of calculation
#                     logger.info(f"Calculation successfully completed: {final_message}")

#                     #display the result
#                     if operation_code == "Percentage":
#                         print(f"{Fore.GREEN}✅ Result of {operation_code} with operands {operand_a} and {operand_b} = {results}%{Style.RESET_ALL}")
#                     else:
#                         print(f"{Fore.GREEN}✅ Result of {operation_code} with operands {operand_a} and {operand_b} = {results}{Style.RESET_ALL}")

#                 except  (InvalidOperation, ValueError) as e:
#                     logger.error(f"Calculation error: {e}")
#                     raise ValidationError(f"Invalid calculation: {e}")

#         # Custom Exception Handling
#         except CommandError as e:
#             print(f"{Fore.RED}⌨️ Command error: {e}{Style.RESET_ALL}")
#             logger.warning(f"⌨️ Command error: {e}")

#         except ValidationError as e:
#             print(f"{Fore.RED}❌ Input Error: {e}{Style.RESET_ALL}")
#             logger.error(f"❌ Validation error: {e}")

#         except OperationError as e:
#             print(f"{Fore.RED}⚠️ Operation Error: {e}{Style.RESET_ALL}")
#             logger.error(f"⚠️ Operation error: {e}")

#         except HistoryError as e:
#             print(f"{Fore.BLUE}📂 History Error: {e}{Style.RESET_ALL}")
#             logger.error(f"📂 History error: {e}")

#         # --- CATCH-ALL FALLBACK ---
#         except Exception as e:
#             print(f"{Fore.RED}{Style.BRIGHT}💥 Unexpected error: {e}{Style.RESET_ALL}")
#             logger.exception("Unhandled exception occurred during REPL loop. 💥 Unexpected error: {e}")
