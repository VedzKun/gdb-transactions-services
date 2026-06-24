from .transaction_exception import TransactionException

class PaymentProcessingError(TransactionException):
    def __init__(self, message="Payment Gateway Rejected Transaction"):
        super().__init__(
            message=message,
            error_code="PAYMENT_GATEWAY_ERROR",
            http_code=400
        )
