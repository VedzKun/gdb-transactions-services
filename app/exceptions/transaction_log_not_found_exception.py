from .transaction_exception import TransactionException

class TransactionLogNotFoundException(TransactionException):
    """Transaction log not found."""
    
    http_code = 404
    error_code = "TRANSACTION_LOG_NOT_FOUND"
