from .transaction_exception import TransactionException

class InsufficientFundsException(TransactionException):
    """Insufficient balance for transaction."""
    
    http_code = 400
    error_code = "INSUFFICIENT_FUNDS"
