from .transaction_exception import TransactionException

class AccountNotActiveException(TransactionException):
    """Account is not active."""
    
    http_code = 400
    error_code = "ACCOUNT_NOT_ACTIVE"
