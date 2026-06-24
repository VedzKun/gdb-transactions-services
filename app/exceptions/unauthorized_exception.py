from .transaction_exception import TransactionException

class UnauthorizedException(TransactionException):
    """User is not authorized for this operation."""
    
    http_code = 401
    error_code = "UNAUTHORIZED"
