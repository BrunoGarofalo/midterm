
from app.logger import logger
from app.exceptions import CommandError

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
                            'Q': ['Exit the program', 'exit']}


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
            logger.warning(f"❌ Invalid operation key: {user_input}")
            raise CommandError(f"❌ Invalid command '{user_input}'. Type 'help' to see available commands.")


