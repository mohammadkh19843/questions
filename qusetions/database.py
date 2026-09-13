import sqlite3
from pathlib import Path

DB_PATH = Path("questions.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT UNIQUE NOT NULL,
                question TEXT NOT NULL,
                options_json TEXT NOT NULL,
                poll_type TEXT NOT NULL,
                correct_option_id INTEGER,
                analysis TEXT DEFAULT '',
                post_text TEXT DEFAULT '',
                telegram_user_id INTEGER,
                status TEXT NOT NULL DEFAULT 'DRAFT',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        conn.commit()


def insert_question(data):
    with get_connection() as conn:
        cursor = conn.execute(
            '''
            INSERT INTO questions (
                content_id, question, options_json, poll_type,
                correct_option_id, analysis, post_text,
                telegram_user_id, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            data,
        )
        conn.commit()
        return cursor.lastrowid
