from .transaction_exception import TransactionException

class ServiceUnavailableException(TransactionException):
    """External service (e.g., Account Service) is unavailable."""
    
    http_code = 503
    error_code = "SERVICE_UNAVAILABLE"
