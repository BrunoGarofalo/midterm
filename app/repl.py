from operation_selection import operationSelection
from app.command_factory import CommandFactory
from decimal import Decimal, InvalidOperation

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
    print('Welcome to the Calculator app!')

    while True:
        selection = operationSelection()
        operation_code = selection.determineOperationCode()

        if operation_code == "exit":
            print("Goodbye!!")
            break

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

                #display the result
                print(f"Result of {operation_code} with operands {operand_a} and {operand_b} = {results}")

            except  Exception as e:
                print(f"Error: {e}")



