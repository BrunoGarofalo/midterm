from app.operation_selection import operationSelection
from app.command_factory import CommandFactory
from decimal import Decimal, InvalidOperation
from app.observers import LoggingObserver, Subject, AutosaveObserver
from datetime import datetime
from app.memento import Originator, CareTaker
from app.logger import logger
from app.math_operations import get_valid_operand
from app.operation_selection import operationSelection
from app.exceptions import OperationError, ValidationError, CommandError, HistoryError

''''
who should delete the history? the logging observer or the originator in the memento?
Should the history be cleared when the instance ends? both the instance history and in the txt file?
Should the redone operation be recalculated? meaning the operands should be re entered?
should the logging observer save the history only when prompted?
Manual save is supposed to save to a CSV? would that override the history saved by the autosave observer?
'''

def main():
    logger.info("Calculator application started")

    caretaker = CareTaker()
    originator = Originator()

    #instantiate and attach observers
    logging_observer = LoggingObserver()
    autosave_observer = AutosaveObserver()

    '''
    I need to simplify, I do not want 2 subjects
    simplify by having originator.attach_observer() and originator internally calls notify whenever add_operation is called
    '''
    subject_logging = Subject()
    subject_autosave = Subject()

    subject_logging.attach(logging_observer)
    subject_autosave.attach(autosave_observer)

    print("👋 Welcome to the Calculator app! Type 'help' to see available commands.")

    while True:
        try:

            # Prompt user for operation
            user_input = input("👉 Select one of the letters corresponding to the operation, IE: A for Percent: ").strip().upper()

            if user_input == "HELP":
                print("\n📜 Available commands, select one of the letters correspondint to the operation, IE: A for Percent:")
                print(operationSelection.show_commands())
                continue

            if user_input not in operationSelection.operations_dictionary:
                # logger.warning(f"❌ CommandError: Invalid command entered by user: {user_input}")
                raise CommandError(f"❌ Command '{user_input}' not recognized. Type 'help' for the list.")

            

            operation_code = operationSelection.operations_dictionary[user_input][1].lower()
            logger.info(f"User selected operation: {operation_code}")

            ################## EXIT #####################
            if operation_code == "exit":
                originator.delete_history()
                logger.info("Application closed!")
                print("Goodbye!!")
                break
            ################## SAVE #####################
            if operation_code=='save':
                logging_observer.save_history(originator.history)
                logger.info("History saved manually to history_log.txt")
                continue

            ################## HISTORY #####################
            if operation_code == 'hist': 
                originator.show_history()
                logger.info("History displayed")
                continue
                
            ################## CLEAR HISTORY #####################
            if operation_code == 'clear':
                # autosave_observer.delete_history()
                originator.delete_history()
                logger.warning("Instance history cleared")
                continue

            ################## UNDO #####################
            if operation_code == 'undo':
                logger.info("Undo requested by user")

                undone_op = caretaker.undo_memento(originator)
                if undone_op:
                    print(f"↩️ Undo performed: {undone_op}")
                    for op in originator.history:
                        subject_autosave.notify(op)
                continue

            ################## REDO #####################
            if operation_code == 'redo':
                logger.info("Redo requested by user")

                redone_op = caretaker.redo_memento(originator)
                if redone_op:
                    print(f"↪️ Redo performed: {redone_op}")
                    for op in originator.history:
                        subject_autosave.notify(op)
                continue


            ################## LOAD #####################
            if operation_code == 'load':
                CSV_history = autosave_observer.load_history()
                originator.get_loaded_history(CSV_history)
                caretaker.save_memento(originator.create_memento()) 
                logger.info("App history loaded from history_log.csv")
                continue


            try:
                operation_obj = CommandFactory(operation_code).createOperationObject()
            except Exception as e:
                logger.error(f"Calculation error: {e}")
                raise OperationError(f"Failed to create operation object: {e}")

            ################## CALCULATIONS #####################
            if hasattr(operation_obj, "calculate"):
                try:
                    # ask user to input operand A
                    operand_a = get_valid_operand("Enter first operand: ")

                    # ask user to input operand B
                    operand_b = get_valid_operand("Enter second operand: ")

                    # # Validate and round operands
                    # operand_a, operand_b = operation_obj.check_decimals(operand_a, operand_b)

                    #Get results
                    results = operation_obj.calculate(operand_a, operand_b)

                    #logger message
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    final_message = f"{timestamp}|{operation_obj.__class__.__name__}|{operand_a}|{operand_b}|{results} "

                    #create memento of current state (before change)
                    caretaker.save_memento(originator.create_memento())

                    #add the new operation (this changes the state)
                    originator.add_operation(final_message)

                    #notify observers
                    subject_autosave.notify(final_message)

                    #Log  successful completion of calculation
                    logger.info(f"Calculation successfully completed: {final_message}")

                    #display the result
                    print(f"✅ Result of {operation_code} with operands {operand_a} and {operand_b} = {results}")

                except  (InvalidOperation, ValueError) as e:
                    logger.error(f"Calculation error: {e}")
                    raise ValidationError(f"Invalid calculation: {e}")

        # Custom Exception Handling
        except CommandError as e:
            print(e)
            logger.warning(f"⌨️ Command error: {e}")

        except ValidationError as e:
            print(f"❌ Input Error: {e}")
            logger.error(f"❌ Validation error: {e}")

        except OperationError as e:
            print(f"⚠️ Operation Error: {e}")
            logger.error(f"⚠️ Operation error: {e}")

        except HistoryError as e:
            print(f"📂 History Error: {e}")
            logger.error(f"📂 History error: {e}")

        # --- CATCH-ALL FALLBACK ---
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            logger.exception("Unhandled exception occurred during REPL loop. 💥 Unexpected error: {e}")
