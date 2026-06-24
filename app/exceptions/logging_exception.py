from .transaction_exception import TransactionException

class LoggingException(TransactionException):
    """Transaction logging failed."""
    
    http_code = 500
    error_code = "LOGGING_ERROR"
