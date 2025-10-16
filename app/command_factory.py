from app.math_operations import Percentage, IntegerDivision, Modulo, Root, Absdifference, Multiplication

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
        if self.user_input == 'percentage':
            print('Percentage object created')
            return Percentage()
        elif self.user_input == 'intdiv':
            return IntegerDivision()
        elif self.user_input == 'modulo':
            return Modulo()
        elif self.user_input == 'root':
            return Root()
        elif self.user_input == 'absdiff':
            return Absdifference()
        elif self.user_input == 'multiplication':
            return Multiplication()
        elif self.user_input == 'hist':
            return History()
        elif self.user_input == 'clear':
            return Clear()
        elif self.user_input == 'undo':
            return Undo()
        elif self.user_input == 'redo':
            return Redo()
        elif self.user_input == 'save':
            return Save()
        elif self.user_input == 'load':
            return Load()
        elif self.user_input == 'help':
            return Help()
        else:
            raise ValueError(f'Command {self.user_input} not allowed, commands allowed: {CalculationTemplate.operations_allowed} ')
        