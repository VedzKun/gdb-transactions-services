from .transaction_exception import TransactionException

class DailyAmountLimitException(TransactionException):
    """Daily amount limit exceeded."""
    
    http_code = 400
    error_code = "DAILY_AMOUNT_LIMIT_EXCEEDED"
