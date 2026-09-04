import math
from db import record_reading, get_recent_readings, log_geofence_event, get_last_confirmed_state
from notifications import notify
import logging

logger = logging.getLogger(__name__)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat1-lat2)
    delta_lamda = math.radians(lon2-lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lamda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def is_within_geofence(
        vehicle_lat: float,
        vehicle_lon: float,
        location_lat: float,
        location_lon: float,
        radius_m: float,
) -> bool:
    distance = haversine_distance(vehicle_lat, vehicle_lon, location_lat, location_lon)
    return distance <= radius_m

async def check_and_log_transition(location_id: int, is_inside: bool, location_name: str = "your location"):
    record_reading(location_id, is_inside)
    last_confirmed = get_last_confirmed_state(location_id)

    if last_confirmed is None:
        event_type = "entered" if is_inside else "exited"
        log_geofence_event(location_id, event_type)
        logger.info(f"Initialized baseline state: {event_type}")
        return None

    if is_inside == last_confirmed:
        return None

    recent = get_recent_readings(location_id, limit=2)
    if len(recent) >= 2 and all(r["is_inside"] == int(is_inside) for r in recent):
        event_type = "entered" if is_inside else "exited"
        log_geofence_event(location_id, event_type)
        logger.info(f"Confirmed transition: {event_type}")

        if event_type == "exited":
            await notify(f"Vehicle left {location_name}")

        return event_type

    logger.info(f"Possible transition detected, waiting for confirmation ({'inside' if is_inside else 'outside'})")
    return None