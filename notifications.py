import os
import httpx


NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


async def notify(message: str, title: str = "Homebound"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            NTFY_URL,
            content=message.encode("utf-8"),
            headers={"Title": title},
        )
    if response.status_code != 200:
        raise RuntimeError(f"Notification failed: {response.text}")