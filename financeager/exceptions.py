"""Module defining expections of the financeager application."""


class FinanceagerException(Exception):
    """Base class for exceptions raised by financeager."""


class PreprocessingError(FinanceagerException):
    """Error raised during preprocessing of user input."""


class InvalidRequest(FinanceagerException):
    """Server indicated invalid request."""


class CommunicationError(FinanceagerException):
    """Error in client-server communication."""


class InvalidConfigError(FinanceagerException):
    """Invalid configuration encountered."""


class ConversionError(FinanceagerException):
    """Invalid input for database conversion."""


class PocketException(FinanceagerException):
    """Base exception for pockets module."""


class PocketValidationFailure(PocketException):
    """Invalid input for pocket backend."""


class PocketEntryNotFound(PocketException):
    """Requested entry not found in database."""
