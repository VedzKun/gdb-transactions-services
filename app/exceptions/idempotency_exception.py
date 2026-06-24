from .transaction_exception import TransactionException

class IdempotencyException(TransactionException):
    """Idempotency key violation."""
    
    http_code = 409
    error_code = "IDEMPOTENCY_CONFLICT"
