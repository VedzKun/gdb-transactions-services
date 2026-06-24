from .transaction_exception import TransactionException

class InvalidTransactionException(TransactionException):
    """Invalid transaction parameters."""
    
    http_code = 400
    error_code = "INVALID_TRANSACTION"
