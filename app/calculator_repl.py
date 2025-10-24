# calculator_repl.py
from decimal import Decimal, InvalidOperation
from datetime import datetime
from colorama import Fore, Style, init
from app.calculator import Calculator
from app.exceptions import CommandError, ValidationError, OperationError, HistoryError
from app.input_validators import get_validated_operand
from app.logger import logger

init(autoreset=True)


def main():
    try:
        # initialize calculator
        calc = Calculator()
        print(f"{Fore.CYAN}👋 Welcome to the Calculator app! Type 'help' to see available commands.{Style.RESET_ALL}")

        while True:
            try:
                # get user input
                user_input = input(
                    f"{Fore.MAGENTA}👉 Select operation (type 'help' to list commands): {Style.RESET_ALL}"
                ).strip().upper()
                logger.info(f"user input entered {user_input}")
                
                # --------------------- HELP COMMAND ----------------------------
                if user_input == "HELP":
                    print(calc.show_commands())
                    continue
                
                # --------------------- GET CODE FOR SELECTED COMMAND ----------------------------
                try:
                    op_code = calc.get_operation_code(user_input).lower()
                except CommandError as e:
                    print(f"{Fore.RED}⌨️ {e}{Style.RESET_ALL}")
                    continue


                # ------------------ EXIT ------------------
                if op_code == "exit":
                    logger.info("👋  Application closed!")
                    print("Application closing. Goodbye!! 👋 ")
                    break

                # ------------------ SAVE ------------------
                if op_code == "save":
                    calc.save_history()
                    continue

                # ------------------ SHOW HISTORY ------------------
                if op_code == "hist":
                    calc.show_history()
                    continue

                # ------------------ CLEAR HISTORY ------------------
                if op_code == "clear":
                    calc.delete_history()
                    continue

                # ------------------ UNDO ------------------
                if op_code == "undo":
                    undone_op = calc.undo()
                    if undone_op:
                        print(f"↩️ Undo performed: {undone_op}")
                    continue

                # ------------------ REDO ------------------
                if op_code == "redo":
                    redone_op = calc.redo()
                    if redone_op:
                        print(f"↪️ Redo performed: {redone_op}")
                    continue

                # ------------------ LOAD ------------------
                if op_code == "load":
                    calc.load_history()
                    calc.show_history()
                    continue

                # ------------------ CALCULATION ------------------
                operation_obj = calc.create_operation(op_code)
                print(f"{Fore.YELLOW}Operation Selected: {operation_obj.__class__.__name__}{Style.RESET_ALL}")

                #-------------------VALIDATE OPERANDS---------------
                operand_a = get_validated_operand("Enter first operand: ")
                operand_b = get_validated_operand("Enter second operand: ")             


                # ---------------------- Perform calculation ---------------------
                result = operation_obj.calculate(operand_a, operand_b)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"{timestamp},{operation_obj.__class__.__name__},{operand_a},{operand_b},{result},{calc.instance_ID}"

                # ----------------------- Update calculator state and observers -------------------
                calc.add_operation(log_message)
                calc.notify_observers(log_message)


                print(f"{Fore.GREEN}✅ Result of {op_code} with operands {operand_a} and {operand_b} = {result}{Style.RESET_ALL}")


            # ------------------ EXCEPTIONS ------------------
            except ValidationError as e:
                print(f"{Fore.RED}❌ Calculator_REPL.py #1 - Input Error: {e}{Style.RESET_ALL}")
            except OperationError as e:
                print(f"{Fore.RED}⚠️ Calculator_REPL.py #2 - Operation Error: {e}{Style.RESET_ALL}")
            except HistoryError as e:
                print(f"{Fore.BLUE}📂 Calculator_REPL.py #3 - History Error: {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}💥 Calculator_REPL.py #4 -  Unexpected error: {e}{Style.RESET_ALL}") # pragma: no cover

    except Exception as e: # pragma: no cover
        # Handle fatal errors during initialization
        print(f"💥 Calculator_REPL.py #5 - Fatal error: {e}")
        logger.error(f"💥 Calculator_REPL.py #5 -Fatal error in calculator REPL: {e}")
        raise

