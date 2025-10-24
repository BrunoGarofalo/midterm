from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from app.logger import logger
from app.config import CALCULATOR_MAX_INPUT_VALUE, CALCULATOR_PRECISION
from app.exceptions import ValidationError, OperationError
from colorama import init, Fore, Style
init(autoreset=True) 
from app.input_validators import validate_nonzero, validate_nonnegative
from app.logger import logger



# ------------------------------------------------------------
# ABS class as template for calculation classes
# ------------------------------------------------------------

class CalculationTemplate(ABC):

    operations_allowed = ['Percentage', 'Multiplication', 'Modulo', 'Root', 'Absolute Difference', 'Integer Division', 'Power']

    @abstractmethod
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal: # pragma: no cover
        #takes in the instance, and inputs a and b as decimals
        '''
        This abstract method runs the selected mathematical operation
        Takes in 2 inputs:
        - a: decimal 
        - b: decimal

        And returns a result as a decimal
        '''
        pass

    def _round_operand(self, operand: Decimal) -> Decimal:
        return operand.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)

    # Ensure both operands (a and b) are within the allowed numeric limits 
    def check_decimals(self, a: Decimal, b: Decimal) -> tuple[Decimal, Decimal]:
        if a > CALCULATOR_MAX_INPUT_VALUE or b > CALCULATOR_MAX_INPUT_VALUE:
            logger.error(f"❌ {e} wrong inputs, Inputs must be ≤ {CALCULATOR_MAX_INPUT_VALUE}")
            raise ValidationError(f"❌ Inputs must be ≤ {CALCULATOR_MAX_INPUT_VALUE}") # pragma: no cover
        try:
            a = self._round_operand(a)
            b = self._round_operand(b)
        except InvalidOperation as e:
            logger.error(f"❌ {e} rounding operands {a}, {b}")
            raise ValidationError(f"Error rounding operands: {e}")
        return a, b

    def _round_result(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal(f"1.{'0'*CALCULATOR_PRECISION}"), rounding=ROUND_HALF_UP)

    # apply round results
    def format_result(self, result: Decimal) -> Decimal:
        try:
            return self._round_result(result)
        except InvalidOperation as e:
            logger.exception("❌ Result formatting failed.")
            raise OperationError(f"❌ Error formatting result: {e}")
    
    def calculate(self, a: Decimal, b: Decimal) -> Decimal:
        try:

            a, b = self.check_decimals(a, b)
            result = self.runOperation(a, b)

            if isinstance(result, Decimal):
                result = self.format_result(result)

            logger.info(f"✅ {self.__class__.__name__} performed: {a} {self._operator_symbol()} {b} = {result}")
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
        
        if b ==0:
            logger.error(f"Percentage calculation failed: {a} / {b}, Cannot perform percent calculation if denominator = 0")
            raise ValidationError('ERROR: Cannot perform percent calculation if denominator = 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return (a/b)*100

class Division(CalculationTemplate):
    def check_decimals(self, a: Decimal, b: Decimal):
        validate_nonzero(b, "Denominator")
        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a/b

class IntegerDivision(CalculationTemplate):
    def check_decimals(self, a: Decimal, b: Decimal):
        
        if b ==0:
            logger.error(f"IntegerDivision check failed: attempted to divide {a} by zero")
            raise ValidationError('ERROR: Cannot perform division by 0')


        return super().check_decimals(a, b)

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
        except Exception as e:   # catch all exceptions
            logger.error(f"❌ Power calculation failed: {a}^{b}")
            raise OperationError(f"❌ Power calculation failed:{a}^{b}, {e}")


class Root(CalculationTemplate):

    def check_decimals(self, a: Decimal, b: Decimal):
      
        validate_nonnegative(a, "Radicand")
        validate_nonzero(b, "Degree of root")
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
       
        if b ==0:
            logger.error(f"Modulo calculation failed: {a} % {b}, modulo cannot take b as 0")
            raise ValueError('ERROR: modulo cannot take b as 0')


        return super().check_decimals(a, b)

    #method to execute the subtraction calculation
    def runOperation(self, a: Decimal, b: Decimal) -> Decimal:
        return a%b


    

