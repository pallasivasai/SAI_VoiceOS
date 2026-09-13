import sqlite3
from .config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            intent TEXT,
            status TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()

def save_command(command, intent, status, message):
    with get_connection() as conn:
        conn.execute("INSERT INTO command_history(command,intent,status,message) VALUES (?,?,?,?)",
                     (command,intent,status,message))
        conn.commit()

def fetch_history(limit=50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT command,intent,status,message,created_at FROM command_history ORDER BY id DESC LIMIT ?",
            (limit,)).fetchall()
    return [dict(r) for r in rows]
