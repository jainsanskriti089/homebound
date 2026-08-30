from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import get_or_create_default_user, get_saved_locations
from vehicle import list_vehicles, get_vehicle_location
from geofence import is_within_geofence, check_and_log_transition
from datetime import datetime, time as dtime

scheduler = AsyncIOScheduler()

BASELINE_MINUTES = 15
ACTIVE_MINUTES = 1 

async def poll_vehicle_location():
    print("\n--- Polling vehicle location ---")
    try:
        user_id = get_or_create_default_user()
        vehicles = await list_vehicles(user_id)

        if not vehicles:
            print("No vehicles found for this user — skipping poll")
            return

        vehicle_id = vehicles[0]["id"]
        lat, lon = await get_vehicle_location(user_id, vehicle_id)
        print(f"Vehicle currently at: {lat}, {lon}")

        locations = get_saved_locations(user_id)
        any_active_window = False
        for loc in locations:
            inside = is_within_geofence(lat, lon, loc["latitude"], loc["longitude"], loc["radius_m"])
            await check_and_log_transition(loc["id"], inside, loc["name"])

            if is_within_expected_window(loc):
                any_active_window = True
        adjust_polling_interval(any_active_window)

    except Exception as e:
        # a single failed poll (car offline, API hiccup, etc.) should never crash
        # the whole scheduler — log it and let the next scheduled poll try again
        print(f"Poll failed, will retry next cycle: {e}")

def adjust_polling_interval(active: bool):
    target_minutes = ACTIVE_MINUTES if active else BASELINE_MINUTES
    job = scheduler.get_job("baseline_poll")

    current_minutes = job.trigger.interval.total_seconds() / 60
    if current_minutes != target_minutes:
        scheduler.reschedule_job("baseline_poll", trigger="interval", minutes=target_minutes)
        print(f"Adjusted polling interval to every {target_minutes} minute(s) (active window: {active})")

def start_scheduler():
    scheduler.add_job(poll_vehicle_location, "interval", minutes=BASELINE_MINUTES, id="baseline_poll", next_run_time=datetime.now())
    scheduler.start()
    print("Scheduler started — polling every 1 minute (test interval)")

def is_within_expected_window(location: dict) -> bool:
    start_str = location.get("expected_leave_start")
    end_str = location.get("expected_leave_end")

    if not start_str or not end_str:
        return False  # no window configured — always use baseline interval

    now = datetime.now().time()
    start = dtime.fromisoformat(start_str)
    end = dtime.fromisoformat(end_str)

    return start <= now <= end