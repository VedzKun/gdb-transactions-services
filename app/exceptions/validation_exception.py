from .transaction_exception import TransactionException

class ValidationException(TransactionException):
    """Input validation failed."""
    
    http_code = 422
    error_code = "VALIDATION_ERROR"
