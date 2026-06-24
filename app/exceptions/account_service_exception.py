from .transaction_exception import TransactionException

class AccountServiceException(TransactionException):
    """Account Service returned an error."""
    
    http_code = 502
    error_code = "ACCOUNT_SERVICE_ERROR"
