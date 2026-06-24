from .transaction_exception import TransactionException

class DatabaseException(TransactionException):
    """Database operation failed."""
    
    http_code = 500
    error_code = "DATABASE_ERROR"
