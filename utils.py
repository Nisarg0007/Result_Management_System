import sqlite3
import os
from datetime import datetime
from cryptography.fernet import Fernet

def log_event(username, role, action):
    """Logs all major events (register, login, CRUD, backup, etc.) in encrypted form."""
    os.makedirs("logs", exist_ok=True)
    log_db = "audit_logs.db"

    # create log table if not exists
    with sqlite3.connect(log_db) as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            role TEXT,
            action TEXT
        )""")

        # encrypt the action text
        key_file = "logs/key.key"
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
        else:
            with open(key_file, "rb") as f:
                key = f.read()
        fernet = Fernet(key)

        encrypted_action = fernet.encrypt(action.encode()).decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("INSERT INTO logs (timestamp, username, role, action) VALUES (?, ?, ?, ?)",
                    (timestamp, username, role, encrypted_action))
        conn.commit()
