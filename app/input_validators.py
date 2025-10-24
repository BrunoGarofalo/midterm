from decimal import Decimal, InvalidOperation
from colorama import Fore, Style
from app.config import CALCULATOR_MAX_INPUT_VALUE
from app.exceptions import ValidationError
from app.logger import logger


def get_valid_operand(prompt: str) -> Decimal:
    """
    Prompt user for a valid decimal operand.
    Keeps asking until a correct, allowed value is entered
    """
    while True:
        # ensures that the value is numeric
        try:
            raw = input(prompt)
            value = Decimal(raw)

        except (InvalidOperation, ValueError):
            logger.info(f"❌ Invalid input '{raw}'")
            print(f"❌ {Fore.MAGENTA}Invalid number. Please try again.{Style.RESET_ALL}")
            continue

        # --- ensures the value entered is within the set range ---
        if abs(value) > CALCULATOR_MAX_INPUT_VALUE:
            print(f"⚠️ {Fore.MAGENTA}Value too large. Max allowed: {CALCULATOR_MAX_INPUT_VALUE}{Style.RESET_ALL}")
            logger.warning(f"❌ Value too large: {value}")
            continue

        return value

def get_validated_operand(prompt: str) -> Decimal:
    """
    Prompt user for a valid decimal operand.
    Only converts input to Decimal and ensures it's numeric.
    """
    while True:
        operand = get_valid_operand(prompt)
        if operand is not None:
            return operand

def validate_nonzero(value: Decimal, var_name: str = "value"):
    """Ensure a given Decimal value is not zero."""
    if value == 0:
        logger.error(f"❌ {var_name} cannot be zero.")
        raise ValidationError(f"{Fore.RED}❌ {var_name.capitalize()} cannot be zero")
    return value


def validate_nonnegative(value: Decimal, var_name: str = "value"):
    """Ensure a given Decimal value is not negative."""
    if value < 0:
        logger.error(f"❌ {var_name} cannot be negative.")
        raise ValidationError(f"{Fore.RED}❌ {var_name.capitalize()} cannot be negative.")
    return value

