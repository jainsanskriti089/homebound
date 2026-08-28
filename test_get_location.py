# test_get_location.py
import asyncio
from dotenv import load_dotenv
load_dotenv()

from db import get_or_create_default_user
from vehicle import list_vehicles, get_vehicle_location

async def main():
    user_id = get_or_create_default_user()
    vehicles = await list_vehicles(user_id)
    vehicle_id = vehicles[0]["id"]

    lat, lon = await get_vehicle_location(user_id, vehicle_id)
    print(f"Latitude: {lat}, Longitude: {lon}")

asyncio.run(main())