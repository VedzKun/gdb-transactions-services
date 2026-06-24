from .transaction_exception import TransactionException

class BothAccountsInactiveException(TransactionException):
    """Both source and destination accounts are inactive."""
    
    http_code = 400
    error_code = "BOTH_ACCOUNTS_INACTIVE"
