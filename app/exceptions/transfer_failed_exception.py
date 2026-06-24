from .transaction_exception import TransactionException

class TransferFailedException(TransactionException):
    """Transfer operation failed."""
    
    http_code = 400
    error_code = "TRANSFER_FAILED"
