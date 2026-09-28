import httpx
from app.config import WEBHOOK_URL
from app.logger import get_logger

logger = get_logger(__name__)


async def send_webhook(event: str, data: dict):
    if not WEBHOOK_URL:
        logger.warning("Webhook URL not configured, skipping")
        return

    payload = {
        "event": event,
        "data": data
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(WEBHOOK_URL, json=payload)
            logger.info(f"Webhook sent | status: {response.status_code}")
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        # We don't raise here — webhook failure should not break the API
