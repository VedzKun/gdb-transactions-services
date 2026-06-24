from .transaction_exception import TransactionException

class InvalidAmountException(TransactionException):
    """Invalid transaction amount."""
    
    http_code = 400
    error_code = "INVALID_AMOUNT"
