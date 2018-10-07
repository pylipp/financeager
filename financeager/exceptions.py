"""Module defining expections of the financeager application."""


class FinanceagerException(Exception):
    """Base class for exceptions raised by financeager."""


class PreprocessingError(FinanceagerException):
    """Error raised during preprocessing of user input."""


class InvalidRequest(FinanceagerException):
    """Server indicated invalid request."""


class CommunicationError(FinanceagerException):
    """Error in client-server communication."""


class OfflineRecoveryError(FinanceagerException):
    """Error during recovering of offline backup."""
