from .transaction_exception import TransactionException

class SameAccountTransferException(TransactionException):
    """Cannot transfer to the same account."""
    
    http_code = 400
    error_code = "SAME_ACCOUNT_TRANSFER"
