from .transaction_exception import TransactionException

class ForbiddenException(TransactionException):
    """User does not have permission for this operation."""
    
    http_code = 403
    error_code = "FORBIDDEN"
