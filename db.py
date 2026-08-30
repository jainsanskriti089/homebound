import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = "homebound.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name, not just index
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tesla_tokens (
            user_id INTEGER REFERENCES users(id),
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            PRIMARY KEY (user_id)
        );

        CREATE TABLE IF NOT EXISTS saved_locations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            radius_m INTEGER NOT NULL,
            UNIQUE(user_id, name)
        );

        CREATE TABLE IF NOT EXISTS geofence_events (
            id INTEGER PRIMARY KEY,
            location_id INTEGER REFERENCES saved_locations(id),
            event_type TEXT NOT NULL,
            occurred_at TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS location_readings (
            id INTEGER PRIMARY KEY,
            location_id INTEGER REFERENCES saved_locations(id),
            is_inside INTEGER NOT NULL,
            recorded_at TIMESTAMP NOT NULL
        );
    """)
    
    conn.commit()
    conn.close()


def get_or_create_default_user():
    """Single-user PoC: ensures one placeholder user row exists, returns its id."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", ("default@local",))
    row = cursor.fetchone()

    if row:
        user_id = row["id"]
    else:
        cursor.execute("INSERT INTO users (email) VALUES (?)", ("default@local",))
        conn.commit()
        user_id = cursor.lastrowid

    conn.close()
    return user_id


def save_tokens(user_id: int, tokens: dict):
    """tokens is the dict returned directly from Tesla's token endpoint."""
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens["expires_in"])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tesla_tokens (user_id, access_token, refresh_token, expires_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            access_token = excluded.access_token,
            refresh_token = excluded.refresh_token,
            expires_at = excluded.expires_at
    """, (user_id, tokens["access_token"], tokens["refresh_token"], expires_at.isoformat()))
    conn.commit()
    conn.close()


def get_tokens(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tesla_tokens WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "access_token": row["access_token"],
        "refresh_token": row["refresh_token"],
        "expires_at": datetime.fromisoformat(row["expires_at"]),
    }

def add_saved_location(user_id: int, name: str, latitude: float, longitude: float, radius_m: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO saved_locations (user_id, name, latitude, longitude, radius_m)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, latitude, longitude, radius_m))
        conn.commit()
        location_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute(
            "SELECT id FROM saved_locations WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        location_id = cursor.fetchone()["id"]
    finally:
        conn.close()

    return location_id

def get_saved_locations(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_locations WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def record_reading(location_id: int, is_inside: bool):
    conn = get_connection()
    conn.execute(
        "INSERT INTO location_readings (location_id, is_inside, recorded_at) VALUES (?, ?, ?)",
        (location_id, int(is_inside), datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()

def get_recent_readings(location_id: int, limit: int = 2):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM location_readings WHERE location_id = ? ORDER BY id DESC LIMIT ?",
        (location_id, limit)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def log_geofence_event(location_id: int, event_type: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO geofence_events (location_id, event_type, occurred_at) VALUES (?, ?, ?)",
        (location_id, event_type, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()

def get_last_confirmed_state(location_id: int):
    """Returns True (inside), False (outside), or None if no events logged yet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT event_type FROM geofence_events WHERE location_id = ? ORDER BY id DESC LIMIT 1",
        (location_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None
    return row["event_type"] == "entered"