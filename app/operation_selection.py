
class operationSelection:

    # Dictory that maps the operation ID to [Operation Name, Short Operation Name]
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
                            'Q': ['Display available commands', 'help'],
                            'R': ['Exit the program', 'exit']}

    user_input_message = "\n".join([f"{key:<2}: {value[0]}" for key, value in operations_dictionary.items()])

    def __init__(self):
        while True:
            self.user_input = input(f'👉 Please select one of the following commands:\n {self.user_input_message}\n').upper()

            if self.user_input in self.operations_dictionary:
                break
            else:
                print(f"❌ Command {self.user_input} not available!")
                

    def determineOperationCode(self):
        self.operation_code = self.operations_dictionary[self.user_input][1].lower()
        print(f"selected command: {self.user_input} - {self.operation_code}")
        return self.operation_code


