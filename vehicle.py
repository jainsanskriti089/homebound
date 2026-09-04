import os
import httpx
from auth import get_valid_access_token
import asyncio

import logging
logger = logging.getLogger(__name__)

API_BASE = os.getenv("TESLA_API_BASE")

class VehicleUnavailableError(Exception):
    """Raised when the vehicle can't be reached right now (offline/asleep timeout) —
    expected to happen periodically, not a real bug."""
    pass

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

async def wake_vehicle(user_id: int, vehicle_id: str):
    access_token = await get_valid_access_token(user_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/api/1/vehicles/{vehicle_id}/wake_up",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if response.status_code != 200:
        raise RuntimeError(f"Wake request failed: {response.text}")

    return response.json()["response"]

async def get_vehicle_data(user_id: int, vehicle_id: str):
    access_token = await get_valid_access_token(user_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/api/1/vehicles/{vehicle_id}/vehicle_data",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"endpoints": "location_data"},
        )

    if response.status_code != 200:
        raise RuntimeError(f"Vehicle data request failed: {response.text}")
    
    return response.json()["response"]

async def get_vehicle_location(user_id: int, vehicle_id: str, max_wake_attempts: int = 10, wait_seconds: int = 5):
    vehicles = await list_vehicles(user_id)
    vehicle = next((v for v in vehicles if str(v["id"]) == str(vehicle_id)), None)
    if vehicle is None:
        raise ValueError(f"Vehicle {vehicle_id} not found for this user")

    if vehicle["state"] != "online":
        logger.info(f"Vehicle state is '{vehicle['state']}' — sending wake request")
        await wake_vehicle(user_id, vehicle_id)

        for attempt in range(max_wake_attempts):
            await asyncio.sleep(wait_seconds)
            vehicles = await list_vehicles(user_id)
            vehicle = next((v for v in vehicles if str(v["id"]) == str(vehicle_id)), None)
            logger.debug(f"  attempt {attempt + 1}: state = {vehicle['state']}")
            if vehicle["state"] == "online":
                logger.info(f"Vehicle woke up after {attempt + 1} check(s)")
                break
        else:
            raise VehicleUnavailableError(f"Vehicle did not wake up in time (last state: {vehicle['state']})")

    data = await get_vehicle_data(user_id, vehicle_id)
    logger.debug("Full drive_state:", data.get("drive_state"))
    drive_state = data["drive_state"]
    return drive_state["latitude"], drive_state["longitude"]