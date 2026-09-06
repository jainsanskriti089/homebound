from fastapi import APIRouter
from db import get_or_create_default_user, get_saved_locations, get_connection, get_tokens
from vehicle import list_vehicles
from auth import get_valid_access_token

router = APIRouter()

@router.get("/api/status")
async def get_status():
    user_id = get_or_create_default_user()

    needs_reauth = False
    vehicle_info = None

    stored_tokens = get_tokens(user_id)
    if stored_tokens is None:
        needs_reauth = True
    else:
        try:
            await get_valid_access_token(user_id)
            vehicles = await list_vehicles(user_id)
            vehicle_info = vehicles[0] if vehicles else None
        except Exception:
            needs_reauth = True

    locations = get_saved_locations(user_id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ge.*, sl.name as location_name
        FROM geofence_events ge
        JOIN saved_locations sl ON ge.location_id = sl.id
        ORDER BY ge.id DESC
        LIMIT 10
    """)

    recent_events = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {
        "needs_reauth": needs_reauth,
        "vehicle": {
            "name": vehicle_info["display_name"] if vehicle_info else None,
            "state": vehicle_info["state"] if vehicle_info else "unknown",
        },
        "locations": locations,
        "recent_events": recent_events,
    }

from pydantic import BaseModel
from db import add_saved_location


class SavedLocationInput(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius_m: int
    expected_leave_start: str | None = None  # e.g. "17:00"
    expected_leave_end: str | None = None


@router.post("/api/locations")
async def create_location(location: SavedLocationInput):
    user_id = get_or_create_default_user()

    location_id = add_saved_location(
        user_id=user_id,
        name=location.name,
        latitude=location.latitude,
        longitude=location.longitude,
        radius_m=location.radius_m,
    )

    # set the expected window if provided, since add_saved_location doesn't currently take it
    if location.expected_leave_start and location.expected_leave_end:
        conn = get_connection()
        conn.execute(
            "UPDATE saved_locations SET expected_leave_start = ?, expected_leave_end = ? WHERE id = ?",
            (location.expected_leave_start, location.expected_leave_end, location_id)
        )
        conn.commit()
        conn.close()

    return {"status": "created", "location_id": location_id}