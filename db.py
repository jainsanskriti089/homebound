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
            radius_m INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS geofence_events (
            id INTEGER PRIMARY KEY,
            location_id INTEGER REFERENCES saved_locations(id),
            event_type TEXT NOT NULL,
            occurred_at TIMESTAMP NOT NULL
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