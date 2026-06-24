from .transaction_exception import TransactionException

class InvalidPINException(TransactionException):
    """PIN is invalid or incorrect."""
    
    http_code = 401
    error_code = "INVALID_PIN"
