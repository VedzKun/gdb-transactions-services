from .transaction_exception import TransactionException

class SourceAccountInactiveException(TransactionException):
    """Source account is inactive."""
    
    http_code = 400
    error_code = "SOURCE_ACCOUNT_INACTIVE"
