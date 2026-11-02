
import sqlite3
from pathlib import Path
from datetime import datetime

# Store the database in the project folder
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "farm_resources.db"

# Initial resource quantities
DEFAULT_RESOURCES = {
    "fertilizer": {"quantity": 500, "unit": "kg"},
    "water": {"quantity": 10000, "unit": "L"},
    "fuel": {"quantity": 500, "unit": "L"}
}


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the resource tables and add initial values if needed."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                name TEXT PRIMARY KEY,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS resource_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_name TEXT NOT NULL,
                quantity_added REAL NOT NULL,
                unit TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        for name, details in DEFAULT_RESOURCES.items():
            connection.execute("""
                INSERT OR IGNORE INTO resources (name, quantity, unit)
                VALUES (?, ?, ?)
            """, (name, details["quantity"], details["unit"]))


def get_resources():
    """Return the current quantities of all resources."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT name, quantity, unit FROM resources"
        ).fetchall()

    return {
        row["name"]: {
            "quantity": row["quantity"],
            "unit": row["unit"]
        }
        for row in rows
    }


def set_resource_quantity(name, quantity):
    """Save a resource quantity after task execution or another update."""
    if name not in DEFAULT_RESOURCES:
        raise ValueError("Unknown resource.")

    if quantity < 0:
        raise ValueError("Resource quantity cannot be negative.")

    with get_connection() as connection:
        connection.execute("""
            UPDATE resources
            SET quantity = ?
            WHERE name = ?
        """, (quantity, name))


def add_resource(name, quantity):
    """Add stock to an existing resource and record the restocking."""
    if name not in DEFAULT_RESOURCES:
        raise ValueError("Select a valid resource.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    unit = DEFAULT_RESOURCES[name]["unit"]

    with get_connection() as connection:
        connection.execute("""
            UPDATE resources
            SET quantity = quantity + ?
            WHERE name = ?
        """, (quantity, name))

        connection.execute("""
            INSERT INTO resource_history
                (resource_name, quantity_added, unit, updated_at)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            quantity,
            unit,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))


def get_resource_history(limit=20):
    """Return the most recent restocking entries."""
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT resource_name, quantity_added, unit, updated_at
            FROM resource_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]
