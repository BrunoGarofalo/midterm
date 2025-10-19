from copy import deepcopy
import pandas as pd
import os
from app.logger import logger
from app.exceptions import HistoryError, FileAccessError, DataFormatError
from colorama import init, Fore, Style
init(autoreset=True) 

class MementoCalculator:
    #hold snapshop in time
    def __init__(self, state):
        try:

            # state set as private variable, deecopy will prevent that the history is modified outside
            '''self._state holds a snapshot of the entire history up to the moment the memento is created
            _state: [5+2=7, 3*4=12, 10-1=9]   <-- snapshot of history at this point'''
            self._state = deepcopy(state)
        
        except Exception as e:
            logger.exception(f"❌ Failed to create memento: {e}")
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
            logger.exception(f"❌ Failed to get memento state: {e}")
            raise HistoryError(f"❌ Failed to get memento state: {e}") from e
    
class Originator: 
    #the object whose state we want to track, holds the current history and creates or restores mementos
    def __init__(self):
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
            logger.error(f"Cannot create memento: {e}")
            raise
    
    def add_operation(self, message):
        #saves new operation to temporary history, IE: "12 - 2 = 10"
        try:
            self.history.append(message)
            logger.info(f"Operation added to history: {message}")

        except Exception as e:
            logger.exception(f"❌ Failed to add operation to history: {e}")
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
            logger.info(f"History restored from memento. Previous: {old_history}, New: {self.history}")

        except Exception as e:
            logger.exception(f"❌ Failed to restore memento: {e}")
            raise HistoryError(f"❌ Failed to restore memento: {e}") from e

    def show_history(self):
        if len(self.history) == 0:
            logger.warning(f"Warning: request history, no history to display!")
            print(f"❌ {Fore.MAGENTA} No history to display!{Style.RESET_ALL}")
        else:
            print("\n👉 Full History:")
            for entry in self.history:
                print(f"{Fore.YELLOW}{entry}{Style.RESET_ALL}")
            logger.info(f"History successfully displayed!")


    def delete_history(self):
        if len(self.history) == 0:
            logger.warning(f"❌ Warning: request to clear history, no history to clear!")
            print(f"❌{Fore.MAGENTA} No instance history to clear!{Style.RESET_ALL}")
        else:
            self.history = []
            logger.warning(f"✅ Instance history succesfully deleted")
            print(f"✅ {Fore.GREEN} Instance history succesfully deleted!{Style.RESET_ALL}")

    def get_loaded_history(self, CSV_history):
        if CSV_history:
            try:
                # CSV_history is a list of operation messages
                self.history = CSV_history.copy()  # to avoid accidental mutation 
                logger.info(f"Warning: History loaded into instance successfully")
                print(f"✅{Fore.GREEN}History loaded into instance successfully.{Style.RESET_ALL}")

            except Exception as e:
                logger.exception(f"❌ Failed to load history into instance: {e}")
                raise DataFormatError(f"❌ Failed to load history: {e}") from e 
        else:
            logger.warning(f"Warning: request to load history from CSV, no history to load!")
            print(f"❌ {Fore.MAGENTA}No history to load from CSV.{Style.RESET_ALL}")
    


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
            # Save current state for comparison
            current_state = originator.history.copy()

            #take the last memento from the stack_undo
            memento = self.stack_undo.pop()

            # add memento for new state to stack_redo
            self.stack_redo.append(originator.create_memento())

            # restore popped memento from stack_undo to history
            originator.restore_memento(memento)

            # Determine which operation was undone
            undone_operations = [op for op in current_state if op not in originator.history]

            undone_op = undone_operations[-1] if undone_operations else None

            if undone_op:
                logger.info(f"Undo performed. Operation undone: {undone_op}")

            # Return the last undone operation if any
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



    
