from fastapi import APIRouter
from db import get_or_create_default_user, get_saved_locations, get_connection
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