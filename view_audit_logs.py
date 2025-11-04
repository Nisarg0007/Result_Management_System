import sqlite3
from cryptography.fernet import Fernet

# Step 1: Load the encryption key from the 'logs/key.key' file
with open("logs/key.key", "rb") as f:
    key = f.read()
fernet = Fernet(key)

# Step 2: Connect to the audit_logs.db database
conn = sqlite3.connect("audit_logs.db")
cur = conn.cursor()

# Step 3: Fetch all the logged events
cur.execute("SELECT timestamp, username, role, action FROM logs ORDER BY id DESC")
rows = cur.fetchall()

# Step 4: Decrypt and print each log entry
print("\n=== AUDIT LOGS (Decrypted & Readable) ===\n")
for ts, user, role, encrypted_action in rows:
    try:
        # Decrypt the action text
        action = fernet.decrypt(encrypted_action.encode()).decode()
    except Exception:
        # If decryption fails (wrong key or corrupted entry)
        action = "[Error decrypting this entry]"
    print(f"[{ts}] {user} ({role}) → {action}")

# Step 5: Close database connection
conn.close()
