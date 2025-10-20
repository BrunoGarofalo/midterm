# calculator_repl.py
from decimal import Decimal, InvalidOperation
from datetime import datetime
from colorama import Fore, Style, init
from app.calculator import Calculator
from app.exceptions import CommandError, ValidationError, OperationError, HistoryError
from app.input_validators import get_valid_operand
from app.logger import logger

init(autoreset=True)

def main():
    try:
        calc = Calculator()
        print(f"{Fore.CYAN}👋 Welcome to the Calculator app! Type 'help' to see available commands.{Style.RESET_ALL}")

        while True:
            try:
                user_input = input(
                    f"{Fore.MAGENTA}👉 Select operation (type 'help' to list commands): {Style.RESET_ALL}"
                ).strip().upper()
                calc.log(f"user input entered {user_input}", "info")
                

                if user_input == "HELP":
                    print(calc.show_commands())
                    continue

                try:
                    op_code = calc.get_operation_code(user_input).lower()
                except CommandError as e:
                    print(f"{Fore.RED}⌨️ {e}{Style.RESET_ALL}")
                    continue

                # ------------------ EXIT ------------------
                if op_code == "exit":
                    calc.delete_history()
                    calc.log("Application closed!", "info")
                    print("Application closing. Goodbye!!")
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
                    print(f"{Fore.YELLOW}✅ History cleared.{Style.RESET_ALL}")
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
                    print(f"{Fore.GREEN}✅ History loaded successfully.{Style.RESET_ALL}")
                    continue

                # ------------------ CALCULATION ------------------
                operation_obj = calc.create_operation(op_code)
                print(f"{Fore.YELLOW}Operation Selected: {operation_obj.__class__.__name__}{Style.RESET_ALL}")

                #-------------------VALIDATE OPERANDS---------------
                operand_a = calc.get_validated_operand("Enter first operand: ", operation_obj)
                operand_b = calc.get_validated_operand("Enter second operand: ", operation_obj, operand_a)

                # Perform calculation
                result = operation_obj.calculate(operand_a, operand_b)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"{timestamp}|{operation_obj.__class__.__name__}|{operand_a}|{operand_b}|{result}"

                # Update calculator state and observers
                # calc.add_operation(log_message)
                # calc.notify_observers(log_message)

                # Display result
                if operation_obj =="Percentage":\
                    print(f"{Fore.GREEN}✅ Result: {result}%{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ Result: {result}{Style.RESET_ALL}")


            # ------------------ EXCEPTIONS ------------------
            except ValidationError as e:
                print(f"{Fore.RED}❌ Input Error: {e}{Style.RESET_ALL}")
            except OperationError as e:
                print(f"{Fore.RED}⚠️ Operation Error: {e}{Style.RESET_ALL}")
            except HistoryError as e:
                print(f"{Fore.BLUE}📂 History Error: {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}💥 Unexpected error: {e}{Style.RESET_ALL}")

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"Fatal error: {e}")
        logger.error(f"Fatal error in calculator REPL: {e}")
        raise

