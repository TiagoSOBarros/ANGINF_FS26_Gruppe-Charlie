import sqlite3
from pathlib import Path

DB_FILE = Path("iss_location.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Location (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                fetched_at INTEGER NOT NULL
            )
        """)
        conn.commit()


def insert_location(latitude: float, longitude: float, fetched_at: int) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO Location (latitude, longitude, fetched_at)
            VALUES (?, ?, ?)
        """, (latitude, longitude, fetched_at))
        conn.commit()


def get_location():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, latitude, longitude, fetched_at
            FROM Location
            ORDER BY fetched_at DESC
            LIMIT 1
        """).fetchone()


def get_all_locations():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, latitude, longitude, fetched_at
            FROM Location
            ORDER BY fetched_at ASC
        """).fetchall()