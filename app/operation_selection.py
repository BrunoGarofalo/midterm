
from app.logger import logger

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

    # user_input_message = "\n".join([f"{key:<2}: {value[0]}" for key, value in operations_dictionary.items()])

    # def __init__(self):
    #     print("👋 Welcome! Type 'help' to see the list of available commands.")
    #     while True:
    #         self.user_input = input(f'👉 Please select one of the following commands:\n {self.user_input_message}\n').upper()

    #         if self.user_input in self.operations_dictionary:
    #             logger.info(f"User selected command: {self.user_input} - {self.operations_dictionary[self.user_input][0]}")
    #             break
    #         else:
    #             logger.warning(f"Invalid command entered by user: {self.user_input}")
    #             print(f"❌ Command {self.user_input} not available!")
                

    # def determineOperationCode(self):
    #     self.operation_code = self.operations_dictionary[self.user_input][1].lower()
    #     logger.info(f"Determined operation code: {self.operation_code} for command {self.user_input}")
    #     print(f"selected command: {self.user_input} - {self.operation_code}")
    #     return self.operation_code

    @classmethod
    def show_commands(cls):
        """Return a formatted string of all available commands."""
        return "\n".join([f"{key:<2}: {value[0]}" for key, value in cls.operations_dictionary.items()])

    @classmethod
    def get_operation_code(cls, user_input: str):
        """Return the operation code (short name) for a given input letter."""
        if user_input in cls.operations_dictionary:
            op_code = cls.operations_dictionary[user_input][1]
            logger.info(f"Determined operation code '{op_code}' for command '{user_input}'")
            return op_code
        else:
            logger.warning(f"Invalid operation key: {user_input}")
            return None


