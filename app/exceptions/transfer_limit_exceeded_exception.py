from .transaction_exception import TransactionException

class TransferLimitExceededException(TransactionException):
    """Daily transfer limit exceeded."""
    
    http_code = 400
    error_code = "TRANSFER_LIMIT_EXCEEDED"
