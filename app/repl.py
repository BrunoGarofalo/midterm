from app.operation_selection import operationSelection
from app.command_factory import CommandFactory
from decimal import Decimal, InvalidOperation
from app.observers import LoggingObserver, Subject, AutosaveObserver
from datetime import datetime
from app.memento import Originator, CareTaker
from app.logger import logger

def get_decimal_input(prompt):
    while True:
        #get user input
        value = input(prompt)
        try:
            #try to convert to decimal, if it fails then the value passed is not a number
            return Decimal(value)
        #return an error if this happens
        except InvalidOperation:
            print("Invalid input. Please enter a numeric value.")

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

    print('Welcome to the Calculator app!')

    while True:
        selection = operationSelection()
        operation_code = selection.determineOperationCode()

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
                operand_a = get_decimal_input("Enter first operand: ")

                # ask user to input operand B
                operand_b = get_decimal_input("Enter second operand: ")

                #Pass operands to check)decimals method to validate that the entries are valid, if not an error will be raised
                operation_obj.check_decimals(operand_a, operand_b)

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



