from .transaction_exception import TransactionException

class DepositFailedException(TransactionException):
    """Deposit operation failed."""
    
    http_code = 400
    error_code = "DEPOSIT_FAILED"
