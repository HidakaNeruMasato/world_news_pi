"""T024 Database Schema Migration Script (scratch/migrate_t024_schema.py)"""

import sqlite3
from world_news.api.database import Pi4Database


def migrate():
    print("Running T024 database migration on worldnews.db...")
    db = Pi4Database("worldnews.db")

    conn = sqlite3.connect("worldnews.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    print(f"PRAGMA integrity_check: {integrity}")

    cursor.execute("PRAGMA table_info(articles)")
    art_cols = [row[1] for row in cursor.fetchall()]
    print(f"Articles columns after migration: {art_cols}")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tables in DB: {tables}")
    conn.close()
    print("Migration completed successfully!")


if __name__ == "__main__":
    migrate()
