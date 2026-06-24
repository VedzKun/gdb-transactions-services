from .transaction_exception import TransactionException

class TransactionLoggingException(TransactionException):
    """Transaction logging operation failed."""
    
    http_code = 500
    error_code = "TRANSACTION_LOGGING_ERROR"
