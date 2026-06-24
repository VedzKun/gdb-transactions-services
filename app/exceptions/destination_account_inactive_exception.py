from .transaction_exception import TransactionException

class DestinationAccountInactiveException(TransactionException):
    """Destination account is inactive."""
    
    http_code = 400
    error_code = "DESTINATION_ACCOUNT_INACTIVE"
