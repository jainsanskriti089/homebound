import os
import httpx
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TESLA_CLIENT_ID")
CLIENT_SECRET = os.getenv("TESLA_CLIENT_SECRET")
API_BASE = os.getenv("TESLA_API_BASE")
TOKEN_URL = "https://auth.tesla.com/oauth2/v3/token"


async def get_partner_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "openid vehicle_device_data vehicle_location",
                "audience": API_BASE,
            },
        )
    if response.status_code != 200:
        raise RuntimeError(f"Partner token failed: {response.text}")
    return response.json()["access_token"]


async def register_domain():
    partner_token = await get_partner_token()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/api/1/partner_accounts",
            headers={"Authorization": f"Bearer {partner_token}"},
            json={"domain": "jainsanskriti089.github.io"},
        )
    if response.status_code != 200:
        raise RuntimeError(f"Domain registration failed: {response.text}")
    return response.json()