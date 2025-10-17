from abc import ABC, abstractmethod
from decimal import Decimal

##################################################################################################################
################## create the abstract class that will serve as the template for all calculation classses ########
##################################################################################################################

class CalculationTemplate(ABC):

    operations_allowed = ['Percentage', 'Multiplication', 'Modulo', 'Root', 'Absolute Difference', 'Integer Division', 'Power']

    @abstractmethod
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal: #takes in the instance, and inputs a and b as decimals
        '''
        This abstract method runs the selected mathematical operation
        Takes in 2 inputs:
        - a: decimal 
        - b: decimal

        And returns a result as a decimal
        '''
        pass

    def check_decimals(self, a: Decimal, b: Decimal) -> Decimal:
        pass

##################################################################################################################
################## create the classes fopr the math calculations
##################################################################################################################
class Addition(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a + b
    
class Subtraction(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a - b
    
class Multiplication(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a * b

class Percentage(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that b isn't 0
        and return a ValueError if it is
        '''
        
        if b ==0:
            raise ValueError('ERROR: Cannot perform percent calculation if denominator = 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return f"{(a/b)*100}%"

class Division(CalculationTemplate):
    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that b isn't 0
        and return a ValueError if it is
        '''
        
        if b ==0:
            raise ValueError('ERROR: Cannot perform division by 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a / b

class IntegerDivision(CalculationTemplate):
    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that b isn't 0
        and return a ValueError if it is
        '''
        
        if b ==0:
            raise ValueError('ERROR: Cannot perform division by 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return int(a // b)
    

class Multiplication(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a * b
    
class Absdifference(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return abs(a - b)
    
class Power(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a ** b


class Root(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that a isn't <0 and b isn't 0
        if they are, return a ValueError
        '''
        
        if a < 0:
            raise ValueError('ERROR: cannot take root of number less than zero')
        
        if b ==0:
            raise ValueError('ERROR: degree of root cannot be 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        self.check_decimals(a, b)
        return a ** (Decimal('1')/b)
    
class Modulo(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that a isn't <0 and b isn't 0
        if they are, return a ValueError
        '''
       
        if b ==0:
            raise ValueError('ERROR: modulo cannot take b as 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        self.check_decimals(a, b)
        return a % b


    

