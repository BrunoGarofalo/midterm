# app/exceptions.py

class CalculatorError(Exception):
    """Base exception for calculator errors."""
    pass


class OperationError(CalculatorError):
    """Raised when an operation fails to execute properly."""
    pass


class ValidationError(CalculatorError):
    """Raised when user input or operand validation fails."""
    pass


class CommandError(CalculatorError):
    """Raised when an invalid or unsupported command is entered."""
    pass


class HistoryError(CalculatorError):
    """Base exception for history-related errors."""
    pass


class FileAccessError(HistoryError):
    """Raised when file read/write operations fail."""
    pass


class DataFormatError(HistoryError):
    """Raised when history data is corrupted or invalid."""
    pass