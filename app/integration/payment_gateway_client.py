import httpx
import logging
from typing import Optional
from app.config.settings import settings

logger = logging.getLogger(__name__)

class PaymentGatewayClient:
    @property
    def BASE_URL(self):
        return f"{settings.PAYMENT_GATEWAY_SERVICE_URL}/api/v1/payment"

    async def validate_payment(
        self, 
        source_account: int, 
        dest_account: int, 
        amount: float, 
        mode: str
    ) -> bool:
        """
        Call Central Payment Gateway for 2nd Level Validation.
        """
        try:
            payload = {
                "source_account_id": source_account,
                "destination_account_id": dest_account,
                "amount": amount,
                "mode": mode,
                "reference_id": None
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.BASE_URL}/process", json=payload, timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("success", False)
                else:
                    logger.error(f"Payment Gateway Error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Payment Gateway Connection Failed: {str(e)}")
            return False

payment_gateway_client = PaymentGatewayClient()
