from copy import deepcopy
import pandas as pd
import os
from app.logger import logger
from app.exceptions import HistoryError, FileAccessError, DataFormatError
from colorama import init, Fore, Style

from app.config import CSV_CARETAKER_HISTORY_FILE, CALCULATOR_HISTORY_DIR, CSV_COLUMNS, CALCULATOR_MAX_HISTORY_SIZE
init(autoreset=True) 

class MementoCalculator:
    #hold snapshop in time
    def __init__(self, state):
        try:

            # state set as private variable, deecopy will prevent that the history is modified outside
            '''self._state holds a snapshot of the entire history up to the moment the memento is created
            _state: [5+2=7, 3*4=12, 10-1=9]   <-- snapshot of history at this point'''
            self._state = deepcopy(state)
            logger.info("✅ Memento succesfully created")
        
        except Exception as e:
            logger.error(f"❌ Failed to create memento: {e}")
            raise HistoryError(f"❌ Failed to create memento: {e}") from e

    def get_state(self):
        #gets the actual history of mementos or history snapshots
        '''
        gets the actual memento
        Mementos (snapshots):
        M1: ["5 + 2 = 7"]
        M2: ["5 + 2 = 7", "3 * 4 = 12"]
        M3: ["5 + 2 = 7", "3 * 4 = 12", "10 - 1 = 9"]

        IE: M2.get_state() returns ["5 + 2 = 7", "3 * 4 = 12"]
        '''
        try:
            return deepcopy(self._state)
        except Exception as e:
            logger.error(f"❌ Failed to get memento state: {e}")
            raise HistoryError(f"❌ Failed to get memento state: {e}") from e
    
class Originator: 
    #the object whose state we want to track, holds the current history and creates or restores mementos
    def __init__(self):
        #self.history holds a list of mementos, M1, M2, M3,...
        self.history = []

    def create_memento(self):
        # create a new memento that reflect the current history state up to that point in time
        '''
        History grows ──▶
        ["5 + 2 = 7"] ──▶ ["5 + 2 = 7", "3 * 4 = 12"] ──▶ ["5 + 2 = 7", "3 * 4 = 12", "10 - 1 = 9"]

        Mementos (snapshots):
        M1: ["5 + 2 = 7"]
        M2: ["5 + 2 = 7", "3 * 4 = 12"]
        M3: ["5 + 2 = 7", "3 * 4 = 12", "10 - 1 = 9"]
        '''
        try:
            return MementoCalculator(self.history)
        
        except HistoryError as e:
            logger.error(f"❌ Cannot create memento: {e}")
            raise HistoryError(f"❌ Failed to create memento {e}") from e
    
    def add_operation(self, message, caretaker=None):
        #saves new operation to temporary history, IE: "12 - 2 = 10"
        try:
            # Save current state to undo stack before adding new operation
            if caretaker:
                caretaker.save_memento(self.create_memento())

            # Add the new operation
            self.history.append(message)
            logger.info(f"✅ Operation added to history: {message}")

            # Trim history if it exceeds max size
            if len(self.history) > CALCULATOR_MAX_HISTORY_SIZE:
                excess = len(self.history) - CALCULATOR_MAX_HISTORY_SIZE
                # keep only the most recent entries
                self.history = self.history[excess:]  
                logger.info(f"⚠️ History exceeded max size; removed oldest {excess} operations")

        except Exception as e:
            logger.error(f"❌ Failed to add operation to history: {e}")
            raise HistoryError(f"❌ Failed to add operation: {e}") from e
    
    def restore_memento(self, memento):
        #restore history from a previous memento
        '''
        updates the current history with the selected memento snapshot
        IE: M2.get_state() returns self.history = ["5 + 2 = 7", "3 * 4 = 12"]
        '''
        try:

            old_history = self.history.copy()
            self.history = memento.get_state()
            logger.info(f"✅ History restored from memento. Previous: {old_history}, New: {self.history}")

        except Exception as e:
            logger.error(f"❌ Failed to restore memento: {e}")
            raise HistoryError(f"❌ Failed to restore memento: {e}") from e



    


class CareTaker:
    # manage stack redo and undo
    '''
    Caretaker does NOT know the details of the state.
    Its job is to store Mementos and let the Originator restore them later.
    It's like a history manager: it keeps track of all the snapshots taken.
    '''
    def __init__(self):
        '''
        An undo stack is basically a history of previous states stored in a last-in, first-out (LIFO) structure,
        usually implemented as a list or stack. Its purpose is to let you go backward in time—undo actions you’ve performed.
        
        How it works: when you perform operations normally. The undo stack grows; the redo stack is empty.
        '''
        self.stack_undo = []

        '''
        The redo stack keeps track of states you can return to after an undo. It's as “forward history”: after you undo something,
        redo lets you reapply that change. Without a redo stack, once you undo, the undone state is lost.
        '''
        self.stack_redo = []
        
        try:

            # Ensure the history directory exists
            os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)
            self.log_file = os.path.join(CALCULATOR_HISTORY_DIR, CSV_CARETAKER_HISTORY_FILE)
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize Caretaker history CSV path  {e}")
            raise FileAccessError(f"❌ Failed to initialize Caretaker history CSV path: {e}")

    def recompose_calculation(self, row):
        return f"{row['timestamp']},{row['operation']},{row['operand1']},{row['operand2']},{row['result']},{row['instance_id']}"

    def save_memento(self, memento):
        try:

            self.stack_undo.append(memento)
            
            #clear stack redo when a new action is done
            self.stack_redo.clear()

            logger.info(f"Memento saved. Undo stack size: {len(self.stack_undo)}; Redo stack cleared")
        except Exception as e:
            logger.exception(f"❌ Failed to save memento: {e}")
            raise HistoryError(f"❌ Failed to save memento: {e}") from e

    def undo_memento(self, originator):

        '''
        Undo: pop from stack_undo → push current state to stack_redo → restore popped memento

        Starting point:
        - history = ["5 + 2 = 7", "3 * 4 = 12"]
        - undo_stack = [ [], ["5 + 2 = 7"] ]
        - redo_stack = []

        When you undo, you:
        - Pop last state from undo stack → ["5 + 2 = 7"]
        - Push current history onto redo stack → ["5 + 2 = 7", "3 * 4 = 12"]
        - Restore popped state → ["5 + 2 = 7"]
        
        - history = ["5 + 2 = 7"]
        - undo_stack = [ [] ]
        - redo_stack = [ ["5 + 2 = 7", "3 * 4 = 12"] ]

        Notice the most recent state is always in the history (top). The previous state is in the undo stack
        '''
        if not self.stack_undo:
            logger.warning("❌ Undo requested but no operation to undo")
            print(f"❌ {Fore.MAGENTA}No operation to undo!{Style.RESET_ALL}")
            return None

        try:
            # Save current state to redo stack
            self.stack_redo.append(originator.create_memento())

            # Pop the previous state from undo stack and restore it
            memento = self.stack_undo.pop()
            originator.restore_memento(memento)

            # Return the last undone operation
            undone_op = None
            if originator.history:
                undone_op = self.stack_redo[-1].get_state()[-1]  # last operation before undo
            return undone_op

        except Exception as e:
            logger.exception(f"❌ Failed to perform undo: {e}")
            raise HistoryError(f"❌ Undo failed: {e}") from e

    def redo_memento(self, originator):
        '''
        Redo: pop from stack_redo → push current state to stack_undo → restore popped memento

        Starting point:
        - history = ["5 + 2 = 7"]
        - undo_stack = [ [] ]
        - redo_stack = [ ["5 + 2 = 7", "3 * 4 = 12"] ]

        When you redo:

        - Pop last state from redo stack → ["5 + 2 = 7", "3 * 4 = 12"]
        - Push current history onto undo stack → ["5 + 2 = 7"]
        - Restore popped state to history → ["5 + 2 = 7", "3 * 4 = 12"]

        - history = ["5 + 2 = 7", "3 * 4 = 12"]
        - undo_stack = [ [], ["5 + 2 = 7"] ]
        - redo_stack = []
        '''
        if not self.stack_redo:
            logger.warning("❌ Red requested but no operation to redo")
            print(f"❌ {Fore.MAGENTA} No operation to redo!{Style.RESET_ALL}")
            return False
        
        try:
            current_state = originator.history.copy()

            #take the last memento from the stack_redo
            memento = self.stack_redo.pop()

            # add memento for new state to stack_redo
            self.stack_undo.append(originator.create_memento())

            # restore popped memento from stack_redo to history
            originator.restore_memento(memento)

            redone_operations = [op for op in originator.history if op not in current_state]

            redone_op = redone_operations[-1] if redone_operations else None

            if redone_op:
                logger.info(f"Redo performed. Operation redone: {redone_op}")

            return redone_op
        
        except Exception as e:
            logger.exception(f"❌ Failed to perform redo: {e}")
            raise HistoryError(f"❌ Redo failed: {e}") from e
        
    def get_loaded_history(self, originator):
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            logger.warning("❌ No CSV history file found to load!")
            print(f"❌ {Fore.MAGENTA}No history file to load.{Style.RESET_ALL}")
            return
        
        if CSV_CARETAKER_HISTORY_FILE:
            try:
                # CSV_CARETAKER_HISTORY_FILE is a list of operation messages
                history_df = pd.read_csv(self.log_file, usecols=CSV_COLUMNS)
                operations = history_df.to_dict(orient="records")

                # Clear current undo/redo stacks
                self.stack_undo.clear()
                self.stack_redo.clear()

                # Reset originator history
                originator.history.clear()

                logger.info(f"✅ Warning: History loaded into instance successfully")
                print(f"✅{Fore.GREEN}History loaded into instance successfully.{Style.RESET_ALL}")

                # Add each operation and create a memento
                for op in operations:
                    originator.add_operation(self.recompose_calculation(op), caretaker=self)

                logger.info(f"✅ Loaded {len(operations)} operations from {self.log_file}")
                print(f"✅ {Fore.GREEN}Loaded {len(operations)} operations into history.{Style.RESET_ALL}")

            except FileAccessError as e:
                raise e
            except Exception as e:
                logger.exception(f"❌ Failed to load history from CSV: {e}")
                raise DataFormatError(f"❌ Failed to load history: {e}") from e
        else:
            logger.warning(f"Warning: request to load history from CSV, no history to load!")
            print(f"❌ {Fore.MAGENTA}No history to load from CSV.{Style.RESET_ALL}")


    def save_history_to_csv(self, originator):
        if not originator.history:
            logger.warning("❌ No history to save!")
            print(f"❌ {Fore.MAGENTA}No history to save.{Style.RESET_ALL}")
            return

        try:
            # Trim history to max size before saving
            history_to_save = originator.history[-CALCULATOR_MAX_HISTORY_SIZE:]

            # Build a list of dictionaries for CSV export
            csv_rows = []
            for entry in history_to_save:
                #  entry is a string like "timestamp,operation,operand1,operand2,result,instance_id"
                parts = entry.split(",")
                if len(parts) != len(CSV_COLUMNS):
                    logger.warning(f"❌ Skipping unproperly formatted entry: {entry}")
                    continue
                row_dict = dict(zip(CSV_COLUMNS, parts))
                csv_rows.append(row_dict)

            # Convert to DataFrame
            df = pd.DataFrame(csv_rows, columns=CSV_COLUMNS)

            # Ensure directory exists
            os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)

            # Save to CSV
            df.to_csv(self.log_file, index=False)
            logger.info(f"✅ Saved {len(csv_rows)} operations to CSV: {self.log_file}")
            print(f"✅ {Fore.GREEN}Saved {len(csv_rows)} operations to CSV.{Style.RESET_ALL}")

        except Exception as e:
            logger.exception(f"❌ Failed to save history to CSV: {e}")
            raise FileAccessError(f"❌ Failed to save history to CSV: {e}") from e

    def delete_saved_history(self, originator: Originator):
        """Delete the saved in memory and CSV persistent history - ONLY AFTER USER CONFIRMATION!."""
        try:
            if os.path.exists(self.log_file):

                # Delete CSV history
                os.remove(self.log_file)
                logger.info(f"✅ Deleted saved history file: {self.log_file}")

                # Clear Originator history
                originator.history.clear()
                logger.info(f"✅ Deleted in-memory history: {self.log_file}")

                print(f"✅ Saved history succesfully deleted")

            else:
                logger.warning(f"⚠️ No saved history file found at {self.log_file}")
        except PermissionError as e:
            logger.error(f"❌ Permission denied deleting CSV history: {e}")
            raise
        except OSError as e:
            logger.error(f"❌ Error deleting CSV history: {e}")
            raise
