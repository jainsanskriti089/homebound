import os
import httpx
from auth import get_valid_access_token

API_BASE = os.getenv("TESLA_API_BASE")


async def list_vehicles(user_id: int):
    access_token = await get_valid_access_token(user_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/api/1/vehicles",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if response.status_code != 200:
        raise RuntimeError(f"Failed to list vehicles: {response.text}")

    return response.json()["response"]