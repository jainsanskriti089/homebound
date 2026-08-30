from dotenv import load_dotenv
load_dotenv()

from db import get_or_create_default_user, add_saved_location, get_saved_locations
from geofence import haversine_distance, is_within_geofence

user_id = get_or_create_default_user()

location_id = add_saved_location(
    user_id=user_id,
    name="Test Location",
    latitude=37.3382,
    longitude=-121.8863,
    radius_m=100,
)
print(f"location_id={location_id}")

locations = get_saved_locations(user_id)
print("Saved locations:", locations)

# Test the math directly with two known points
loc = locations[0]
test_vehicle_lat = 37.3382   # same as location — should be "inside"
test_vehicle_lon = -121.8863

distance = haversine_distance(test_vehicle_lat, test_vehicle_lon, loc["latitude"], loc["longitude"])
print(f"Distance: {distance:.2f} meters")

inside = is_within_geofence(test_vehicle_lat, test_vehicle_lon, loc["latitude"], loc["longitude"], loc["radius_m"])
print(f"Is within geofence: {inside}")

# add to the bottom of test_geofence.py

print("\n--- Testing outside the geofence ---")

# Roughly 1km away from your test location (adjust based on your actual coordinates)
# Rule of thumb: 0.01 degrees of latitude ≈ 1.1km
far_lat = loc["latitude"] + 0.01
far_lon = loc["longitude"]

distance = haversine_distance(far_lat, far_lon, loc["latitude"], loc["longitude"])
print(f"Distance: {distance:.2f} meters")

inside = is_within_geofence(far_lat, far_lon, loc["latitude"], loc["longitude"], loc["radius_m"])
print(f"Is within geofence: {inside}")

print("\n--- Testing right at the boundary ---")

# Nudge just slightly — small enough to land close to your 100m radius
# This isn't exact science, just close enough to see the behavior near the edge
near_lat = loc["latitude"] + 0.0009  # roughly ~100m north
near_lon = loc["longitude"]

distance = haversine_distance(near_lat, near_lon, loc["latitude"], loc["longitude"])
print(f"Distance: {distance:.2f} meters")

inside = is_within_geofence(near_lat, near_lon, loc["latitude"], loc["longitude"], loc["radius_m"])
print(f"Is within geofence: {inside}")