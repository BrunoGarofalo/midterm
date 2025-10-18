from app.operation_selection import operationSelection
from app.command_factory import CommandFactory
from decimal import Decimal, InvalidOperation
from app.observers import LoggingObserver, Subject, AutosaveObserver
from datetime import datetime
from app.memento import Originator, CareTaker
from app.logger import logger
from app.math_operations import get_valid_operand
from app.operation_selection import operationSelection

''''
who should delete the history? the logging observer or the originator in the memento?
Should the history be cleared when the instance ends? both the instance history and in the txt file?
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

        # Prompt user for operation
        user_input = input("👉 Select one of the letters corresponding to the operation, IE: A for Percent: ").strip().upper()

        if user_input == "HELP":
            print("\n📜 Available commands, select one of the letters correspondint to the operation, IE: A for Percent:")
            print(operationSelection.show_commands())
            continue

        if user_input not in operationSelection.operations_dictionary:
            print(f"❌ Command '{user_input}' not recognized. Type 'help' for the list.")
            logger.warning(f"Invalid command entered by user: {user_input}")
            continue
        

        operation_code = operationSelection.operations_dictionary[user_input][1].lower()
        print(operation_code)
        # selection = operationSelection()
        # operation_code = selection.determineOperationCode()

        if operation_code == "exit":
            originator.delete_history()
            logger.info("Application closed!")
            print("Goodbye!!")
            break

        if operation_code=='save':
            logging_observer.save_history(originator.history)
            logger.info("History saved manually to history_log.txt")
            continue

        # show history of logging observer
        if operation_code == 'hist': 
            originator.show_history()
            logger.info("History displayed")
            continue
            
        #clear history of logging observer
        if operation_code == 'clear':
            # autosave_observer.delete_history()
            originator.delete_history()
            logger.warning("Instance history cleared")
            continue


        if operation_code == 'undo':
            logger.info("Undo requested by user")

            undone_op = caretaker.undo_memento(originator)
            if undone_op:
                print(f"↩️ Undo performed: {undone_op}")
                for op in originator.history:
                    subject_autosave.notify(op)
            continue

        if operation_code == 'redo':
            logger.info("Redo requested by user")

            redone_op = caretaker.redo_memento(originator)
            if redone_op:
                print(f"↪️ Redo performed: {redone_op}")
                for op in originator.history:
                    subject_autosave.notify(op)
            continue


        # load history from autosave observer to logging observer
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
            print(f"Error creating operation: {e}")
            continue

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

            except  Exception as e:
                logger.error(f"Calculation error: {e}")
                print(f"❌ Error: {e}")



