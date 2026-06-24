from .transaction_exception import TransactionException

class InvalidAccountException(TransactionException):
    """Account is invalid or malformed."""
    
    http_code = 400
    error_code = "INVALID_ACCOUNT"
