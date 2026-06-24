from .transaction_exception import TransactionException

class InvalidTransferModeException(TransactionException):
    """Invalid transfer mode specified."""
    
    http_code = 400
    error_code = "INVALID_TRANSFER_MODE"
