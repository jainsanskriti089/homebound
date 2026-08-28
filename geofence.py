import math

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