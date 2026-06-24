from .transaction_exception import TransactionException

class TransferLimitNotFoundException(TransactionException):
    """Transfer limit not found for account."""
    
    http_code = 404
    error_code = "TRANSFER_LIMIT_NOT_FOUND"
