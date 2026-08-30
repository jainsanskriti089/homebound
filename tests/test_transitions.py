import asyncio
from dotenv import load_dotenv
load_dotenv()

from db import get_or_create_default_user, get_saved_locations
from geofence import check_and_log_transition


async def main():
    user_id = get_or_create_default_user()
    location = get_saved_locations(user_id)[0]
    location_id = location["id"]
    location_name = location["name"]

    # Simulated sequence: inside, inside, outside (jitter - single blip), inside, outside, outside (real exit)
    sequence = [True, True, False, True, False, False]

    for i, is_inside in enumerate(sequence):
        print(f"\nReading {i+1}: {'inside' if is_inside else 'outside'}")
        result = await check_and_log_transition(location_id, is_inside, location_name)
        if result:
            print(f"  >>> EVENT FIRED: {result}")


asyncio.run(main())