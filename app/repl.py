from app.operation_selection import operationSelection
from app.command_factory import CommandFactory
from decimal import Decimal, InvalidOperation
from app.observers import LoggingObserver, Subject, AutosaveObserver
from datetime import datetime
from app.memento import MementoCalculator, Originator, CareTaker

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
            print("Goodbye!!")
            break

        if operation_code=='save':
            logging_observer.save_history(originator.history)
            continue

        # show history of logging observer
        if operation_code == 'hist': 
            originator.show_history()
            continue
            
        #clear history of logging observer
        if operation_code == 'clear':
            # autosave_observer.delete_history()
            originator.delete_history()
            continue

        # load history from autosave observer to logging observer
        if operation_code == 'load':
            history = autosave_observer.load_history()
            logging_observer.history = history
            print('History loaded!')
            continue


        try:
            operation_obj = CommandFactory(operation_code).createOperationObject()
        except Exception as e:
            print(f"Error creating operation: {e}")
            continue

        if hasattr(operation_obj, "runOperation"):
            try:
                # ask user to input operand A
                operand_a = get_decimal_input("Enter first operand: ")

                # ask user to input operand B
                operand_b = get_decimal_input("Enter second operand: ")

                #Pass operands to check)decimals method to validate that the entries are valid, if not an error will be raised
                operation_obj.check_decimals(operand_a, operand_b)

                #Get results
                results = operation_obj.runOperation(operand_a, operand_b)

                #logger message
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                final_message = f"{timestamp}|{operation_obj.__class__.__name__}|{operand_a}|{operand_b}|{results} "

                #create memento of current state (before change)
                caretaker.save_memento(originator.create_memento())

                #add the new operation (this changes the state)
                originator.add_operation(final_message)

                #notify observers
                subject_autosave.notify(final_message)
                # subject_logging.notify(final_message)

                print(final_message)

                #display the result
                print(f"✅ Result of {operation_code} with operands {operand_a} and {operand_b} = {results}")

            except  Exception as e:
                print(f"❌ Error: {e}")



