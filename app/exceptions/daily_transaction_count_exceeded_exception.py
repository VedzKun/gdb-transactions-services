from .transaction_exception import TransactionException

class DailyTransactionCountExceededException(TransactionException):
    """Daily transaction count limit exceeded."""
    
    http_code = 400
    error_code = "DAILY_TRANSACTION_COUNT_EXCEEDED"
