from app.math_operations import Percentage, IntegerDivision, Modulo, Root, Absdifference, Multiplication, Addition, Division, Subtraction, Power
from app.math_operations import CalculationTemplate
from app.logger import logger
from app.exceptions import CommandError

class CommandFactory:
    #initialize instance
    def __init__(self, user_input):
        self.user_input = user_input
    '''
    Need to ensure user_input is passed correctly, input will be selected using unique IDs to ensure no mismatches occur, IE:

    A = Multiplication
    B = Integer Division
    etc...
    '''

    #create operation object based on user input, also handles operation mismatches
    def createOperationObject(self):
        try:
            if self.user_input == 'percentage':
                return Percentage()
            elif self.user_input == 'add':
                return Addition()
            elif self.user_input == 'subtract':
                return Subtraction()
            elif self.user_input == 'div':
                return Division()
            elif self.user_input == 'intdiff':
                return IntegerDivision()
            elif self.user_input == 'modulo':
                return Modulo()
            elif self.user_input == 'root':
                return Root()
            elif self.user_input == 'absdiff':
                return Absdifference()
            elif self.user_input == 'multiplication':
                return Multiplication()
            elif self.user_input == 'power':
                return Power()
            # elif self.user_input == 'help':
            #     return Help()
            else:
                logger.error(f"❌ Value error: Command {self.user_input} not allowed")
                raise CommandError(f"❌ Command '{self.user_input}' not allowed. Allowed commands: {CalculationTemplate.operations_allowed}"
                )
        except Exception as e:
            logger.exception(f"Failed to create operation object for '{self.user_input}': {e}")
            raise
        