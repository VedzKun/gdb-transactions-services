from .transaction_exception import TransactionException

class WithdrawalFailedException(TransactionException):
    """Withdrawal operation failed."""
    
    http_code = 400
    error_code = "WITHDRAWAL_FAILED"
