import os
import httpx
import logging

NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

logger = logging.getLogger(__name__)

async def notify(message: str, title: str = "Homebound"):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                NTFY_URL,
                content=message.encode("utf-8"),
                headers={"Title": title},
            )
        if response.status_code != 200:
            logger.error(f"Notification failed with status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Notification request failed entirely: {e}")