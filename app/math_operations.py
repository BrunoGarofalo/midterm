from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from app.logger import logger
from app.config import CALCULATOR_MAX_INPUT_VALUE, CALCULATOR_PRECISION
from app.exceptions import ValidationError, OperationError
from colorama import init, Fore, Style
init(autoreset=True) 


# ------------------------------------------------------------
# INPUT VALIDATION
# ------------------------------------------------------------
def get_valid_operand(prompt):
    while True:
        #get user input
        
        try:
            #try to convert to decimal, if it fails then the value passed is not a number
            value = Decimal(input(prompt))
        #return an error if this happens
        except InvalidOperation:
            logger.warning(f"❌ Invalid input {prompt}. Please enter a numeric value.")
            print(f"❌ {Fore.MAGENTA} Invalid input {prompt}. Please enter a numeric value.{Style.RESET_ALL}")
            continue

        if value > CALCULATOR_MAX_INPUT_VALUE:
            logger.warning(f"❌ Input too large {prompt}")
            print(f"❌ {Fore.MAGENTA} Input too large. Maximum allowed is {CALCULATOR_MAX_INPUT_VALUE}. Try again.{Style.RESET_ALL}")
            continue

        return value

# ------------------------------------------------------------
# ABS class as template for calculation classes
# ------------------------------------------------------------

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
            logger.warning(f"❌ Input exceeds max value of {CALCULATOR_MAX_INPUT_VALUE}: {a}, {b}")
            raise ValidationError(f"❌ Inputs must be ≤ {CALCULATOR_MAX_INPUT_VALUE}")
        try:
            # Round inputs according to precision
            a = a.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)
            b = b.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)
            
        except InvalidOperation as e:
            logger.exception(f"❌ rounding operation failed {e}")
            raise ValidationError(f"Error rounding operands: {e}")
        
        return a, b

    def format_result(self, result: Decimal) -> Decimal:
        try:
            return result.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)
        except InvalidOperation as e:
            logger.exception("❌ Result formatting failed.")
            raise OperationError(f"❌ Error formatting result: {e}")
    
    def calculate(self, a: Decimal, b: Decimal) -> Decimal:
        try:

            a, b = self.check_decimals(a, b)
            result = self.runOperation(a, b)

            if isinstance(result, Decimal):
                result = self.format_result(result)

            logger.info(f"{self.__class__.__name__} performed: {a} {self._operator_symbol()} {b} = {result}")
            return result
        
        except Exception as e:
            logger.exception("❌ Unexpected error during calculation.")
            raise OperationError(f"❌ Unexpected error: {e}")

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
        try:
            return a ** b
        except InvalidOperation as e:
            logger.error(f"❌ Power calculation failed: {a}^{b}")
            raise OperationError(f"❌ Power calculation failed:{a}^{b}, {e}")


class Root(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
        '''
        Change the parent method check_decimals so that it checks that a isn't <0 and b isn't 0
        if they are, return a ValueError
        '''
        
        if a < 0:
            logger.error(f"❌ Invalid root attempt: root({a}, {b}), cannot take root of number less than zero")
            raise ValidationError('❌ ERROR: cannot take root of number less than zero')
        
        if b ==0:
            logger.error(f"❌ Invalid root degree: root({a}, {b}), degree of root cannot be 0")
            raise ValidationError('❌ ERROR: degree of root cannot be 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        try:
            return a ** (Decimal("1") / b)
        except InvalidOperation as e:
            logger.exception("❌ Root calculation failed.")
            raise OperationError(f"❌ Root calculation failed:{a}, {b}, {e}")
    
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


    

