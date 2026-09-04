import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import asyncio
import db as db_module


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Points db.py at a temporary, throwaway SQLite file for the duration of each test,
    so tests never touch your real homebound.db."""
    test_db_path = tmp_path / "test_homebound.db"
    monkeypatch.setattr(db_module, "DB_PATH", str(test_db_path))
    db_module.init_db()

    from db import add_saved_location
    location_id = add_saved_location(
        user_id=1, name="Test Location", latitude=37.3382, longitude=-121.8863, radius_m=100
    )
    return location_id


def test_single_jitter_blip_does_not_fire(test_db, monkeypatch):
    """A single outside reading surrounded by inside readings should never fire an event."""
    import geofence

    async def fake_notify(message, title="Homebound"):
        pass  # don't actually send real notifications during tests

    monkeypatch.setattr(geofence, "notify", fake_notify)

    async def run():
        results = []
        sequence = [True, True, False, True]  # single blip, no confirmed exit
        for is_inside in sequence:
            result = await geofence.check_and_log_transition(test_db, is_inside, "Test Location")
            results.append(result)
        return results

    results = asyncio.run(run())
    assert all(r is None for r in results), "No event should fire from a single jitter blip"


def test_confirmed_exit_fires_exactly_once(test_db, monkeypatch):
    """Two consecutive outside readings should fire exactly one 'exited' event."""
    import geofence

    async def fake_notify(message, title="Homebound"):
        pass

    monkeypatch.setattr(geofence, "notify", fake_notify)

    async def run():
        results = []
        sequence = [True, True, False, False]  # confirmed exit on the 4th reading
        for is_inside in sequence:
            result = await geofence.check_and_log_transition(test_db, is_inside, "Test Location")
            results.append(result)
        return results

    results = asyncio.run(run())
    fired_events = [r for r in results if r is not None]
    assert fired_events == ["exited"], "Exactly one 'exited' event should fire, on the 4th reading"