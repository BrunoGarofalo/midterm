from abc import ABC, abstractmethod
from decimal import Decimal
from app.logger import logger

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
        result = a + b
        logger.info(f"Addition performed: {a} + {b} = {result}")
        return result
    
class Subtraction(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        result = a - b
        logger.info(f"Subtraction performed: {a} - {b} = {result}")
        return result
    
class Multiplication(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        result = a * b
        logger.info(f"Multiplication performed: {a} * {b} = {result}")
        return a * b

class Percentage(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that b isn't 0
        and return a ValueError if it is
        '''
        
        if b ==0:
            logger.error(f"Percentage calculation failed: {a} / {b}, Cannot perform percent calculation if denominator = 0")
            raise ValueError('ERROR: Cannot perform percent calculation if denominator = 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        result = (a/b)*100
        logger.info(f"Percentage performed: ({a} / {b}) * 100 = {result}%")
        return f"{result}%"

class Division(CalculationTemplate):
    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that b isn't 0
        and return a ValueError if it is
        '''
        
        if b ==0:
            logger.error(f"Division by zero attempt: {a} / {b}, Cannot perform division by 0")
            raise ValueError('ERROR: Cannot perform division by 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:

        result = a/b
        logger.info(f"Division performed: {a} / {b} = {result}")

        return result

class IntegerDivision(CalculationTemplate):
    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that b isn't 0
        and return a ValueError if it is
        '''
        
        if b ==0:
            logger.error(f"IntegerDivision check failed: attempted to divide {a} by zero")
            raise ValueError('ERROR: Cannot perform division by 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        result = int(a // b)
        logger.info(f"IntegerDivision performed: {a} // {b} = {result}")

        return result
    

class Multiplication(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        result = a * b
        logger.info(f"Multiplication performed: {a} * {b} = {result}")

        return result
    
class Absdifference(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        result = abs(a - b)
        logger.info(f"Absolute Difference performed: |{a} - {b}| = {result}")
        return result
    
class Power(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        result = a ** b
        logger.info(f"Power performed: {a} ** {b} = {result}")

        return result


class Root(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that a isn't <0 and b isn't 0
        if they are, return a ValueError
        '''
        
        if a < 0:
            logger.error(f"Invalid root attempt: root({a}, {b}), cannot take root of number less than zero")
            raise ValueError('ERROR: cannot take root of number less than zero')
        
        if b ==0:
            logger.error(f"Invalid root degree: root({a}, {b}), degree of root cannot be 0")
            raise ValueError('ERROR: degree of root cannot be 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        self.check_decimals(a, b)

        result = a ** (Decimal('1') / b)
        logger.info(f"Root performed: {b}-th root of {a} = {result}")

        return result
    
class Modulo(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that a isn't <0 and b isn't 0
        if they are, return a ValueError
        '''
       
        if b ==0:
            logger.error(f"Modulo calculation failed: {a} % {b}, modulo cannot take b as 0")
            raise ValueError('ERROR: modulo cannot take b as 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        self.check_decimals(a, b)
        result = a % b
        logger.info(f"Modulo performed: {a} % {b} = {result}")

        return result


    

