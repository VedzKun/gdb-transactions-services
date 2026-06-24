from .transaction_exception import TransactionException

class AccountNotFoundException(TransactionException):
    """Account does not exist."""
    
    http_code = 404
    error_code = "ACCOUNT_NOT_FOUND"
