import httpx
import logging
from typing import Optional
from app.config.settings import settings

logger = logging.getLogger(__name__)

class NotificationClient:
    @property
    def BASE_URL(self):
        return f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notify"

    async def send_notification(self, recipient: str, message: str, type: str = "INFO", mode: Optional[str] = None):
        try:
            payload = {
                "recipient": recipient,
                "message": message,
                "type": type,
                "mode": mode
            }
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.BASE_URL}/send", json=payload, timeout=2.0)
        except Exception as e:
            logger.warning(f"Failed to send notification: {str(e)}")

notification_client = NotificationClient()
