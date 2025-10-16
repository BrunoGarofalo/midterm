from operation_selection import operationSelection
from app.command_factory import CommandFactory


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
                operand_a = float(input("Enter first operand: "))

                # ask user to input operand B
                operand_b = float(input("Enter second operand: "))

                #Pass operands to check)decimals method to validate that the entries are valid, if not an error will be raised
                operation_obj.check_decimals(operand_a, operand_b)

                #Get results
                results = operation_obj.runOperation(operand_a, operand_b)

                #display the result
                print(f"Result: {results}")

            except  Exception as e:
                print(f"Error: {e}")


        # factory = CommandFactory(selectedOperationcode)

        # operation_object = factory.createOperationObject()


main()