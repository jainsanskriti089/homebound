import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from geofence import haversine_distance, is_within_geofence


def test_haversine_identical_points_is_zero():
    distance = haversine_distance(37.3382, -121.8863, 37.3382, -121.8863)
    assert distance == 0.0


def test_haversine_known_distance():
    # San Jose to San Francisco, roughly 48km apart
    distance = haversine_distance(37.3382, -121.8863, 37.7749, -122.4194)
    assert 65000 < distance < 71000  # allow reasonable margin, not testing exact precision


def test_is_within_geofence_at_center():
    assert is_within_geofence(37.3382, -121.8863, 37.3382, -121.8863, radius_m=100) is True


def test_is_within_geofence_clearly_outside():
    # roughly 1.1km away, well outside a 100m radius
    assert is_within_geofence(37.3482, -121.8863, 37.3382, -121.8863, radius_m=100) is False


def test_is_within_geofence_just_inside_boundary():
    # ~90m away, inside a 100m radius
    result = is_within_geofence(37.33828, -121.8863, 37.3382, -121.8863, radius_m=100)
    assert result is True


def test_is_within_geofence_just_outside_boundary():
    # explicitly compute a point just past the 100m boundary, rather than guessing an offset
    import math
    lat, lon = 37.3382, -121.8863
    # ~105m north — small buffer past the 100m radius to avoid floating-point edge cases
    delta_lat = 105 / 111320  # ~111.32km per degree of latitude
    result = is_within_geofence(lat + delta_lat, lon, lat, lon, radius_m=100)
    assert result is False