from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from app.logger import logger
from app.config import CALCULATOR_MAX_INPUT_VALUE, CALCULATOR_PRECISION

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
        """Generic check for input bounds."""
        if a > CALCULATOR_MAX_INPUT_VALUE or b > CALCULATOR_MAX_INPUT_VALUE:
            logger.warning(f"Input exceeds max value: {a}, {b}")
            raise ValueError(f"Inputs must be ≤ {CALCULATOR_MAX_INPUT_VALUE}")
        # Round inputs according to precision
        a = a.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)
        b = b.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)
        return a, b
    
    def format_result(self, result: Decimal) -> Decimal:
        """Round result according to CALCULATOR_PRECISION."""
        return result.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)
    
    def calculate(self, a: Decimal, b: Decimal) -> Decimal:

        a, b = self.check_decimals(a, b)


        result = self.runOperation(a, b)


        if isinstance(result, Decimal):
            result = self.format_result(result)


        logger.info(f"{self.__class__.__name__} performed: {a} {self._operator_symbol()} {b} = {result}")
        return result

    def _operator_symbol(self) -> str:
        """Symbol for logging purposes."""
        mapping = {
            "Addition": "+",
            "Subtraction": "-",
            "Multiplication": "*",
            "Division": "/",
            "IntegerDivision": "//",
            "Modulo": "%",
            "Power": "**",
            "Root": "root",
            "Percentage": "%",
            "Absdifference": "|a-b|"
        }
        return mapping.get(self.__class__.__name__, "?")

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
            logger.error(f"Percentage calculation failed: {a} / {b}, Cannot perform percent calculation if denominator = 0")
            raise ValueError('ERROR: Cannot perform percent calculation if denominator = 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return (a/b)

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
        return a/b

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
        return int(a//b)
    
class Absdifference(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return abs(a - b)
    
class Power(CalculationTemplate):

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        a, b = self.check_decimals(a, b)
        result = a ** b
        result = self.format_result(result)
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
        return a ** (Decimal('1') / b)
    
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
        return a%b


    

