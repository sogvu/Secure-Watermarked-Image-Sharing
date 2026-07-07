import sqlite3, os
from contextlib import contextmanager
from config import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "database", "app.db")

@contextmanager
def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')),
                event       TEXT    NOT NULL,
                image_id    TEXT,
                filename    TEXT,
                owner_id    TEXT,
                receiver_id TEXT,
                detail      TEXT,
                result      TEXT    DEFAULT 'SUCCESS'
            )""")

def log_audit(event: str, image_id=None, filename=None,
              owner_id=None, receiver_id=None, detail=None, result="SUCCESS"):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO audit_log
              (event, image_id, filename, owner_id, receiver_id, detail, result)
            VALUES (?,?,?,?,?,?,?)
        """, (event, image_id, filename, owner_id, receiver_id, detail, result))

def get_audit_log(image_id: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE image_id=? ORDER BY id ASC",
            (image_id,)).fetchall()
        return [dict(r) for r in rows]

def get_all_images():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT DISTINCT image_id, filename, owner_id, receiver_id,
                   MIN(timestamp) as created_at
            FROM audit_log WHERE image_id IS NOT NULL
            GROUP BY image_id ORDER BY created_at DESC
        """).fetchall()
        return [dict(r) for r in rows]