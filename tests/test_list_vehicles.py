"""
Quick test script: confirms the currently-stored account's tokens can
successfully list vehicles via the Tesla Fleet API.

Run this after any new /login authorization to confirm the flow worked
end-to-end and real vehicle data comes back.

Usage:
    python test_list_vehicles.py
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from db import get_or_create_default_user
from vehicle import list_vehicles


async def main():
    user_id = get_or_create_default_user()
    print(f"Checking vehicles for user_id={user_id}...\n")

    try:
        vehicles = await list_vehicles(user_id)
    except Exception as e:
        print(f"Failed to list vehicles: {e}")
        return

    if not vehicles:
        print("No vehicles returned. This usually means either:")
        print("   - The authorized account has no Tesla linked, or")
        print("   - /login hasn't been completed yet for this account")
        return

    print(f"Found {len(vehicles)} vehicle(s):\n")
    for v in vehicles:
        print(f"  ID:      {v['id']}")
        print(f"  VIN:     {v['vin']}")
        print(f"  Name:    {v['display_name']}")
        print(f"  State:   {v['state']}")
        print()


if __name__ == "__main__":
    asyncio.run(main())