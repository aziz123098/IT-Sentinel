import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "incidents.db"

def connect():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'Open',
                source TEXT NOT NULL DEFAULT 'Simulation',
                created_at TEXT NOT NULL
            )
        """)

def save_incident(check_name, severity, details, source="Simulation"):
    initialize_database()
    with connect() as conn:
        conn.execute("""
            INSERT INTO incidents
            (check_name, severity, details, source, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (check_name, severity, details, source, datetime.now(timezone.utc).isoformat()))

def get_incidents():
    initialize_database()
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM incidents ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

def resolve_incident(incident_id):
    initialize_database()
    with connect() as conn:
        cursor = conn.execute("""
            UPDATE incidents SET status = 'Resolved'
            WHERE id = ? AND status = 'Open'
        """, (incident_id,))
        return cursor.rowcount > 0
