import sqlite3
from datetime import datetime


def init_db(db_path: str):
    """
    Creates the SQLite database and scores table if they do not exist.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def insert_score(db_path: str, player: str, attempts: int):
    """
    Inserts a new score into the database.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scores (player, attempts, created_at) VALUES (?, ?, ?)",
            (player, attempts, datetime.utcnow().isoformat())
        )
        conn.commit()


def get_top_scores(db_path: str, limit: int = 10):
    """
    Returns the best scores ordered by attempts (ascending).
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT player, attempts, created_at
            FROM scores
            ORDER BY attempts ASC, created_at ASC
            LIMIT ?
            """,
            (limit,)
        )
        return cursor.fetchall()
