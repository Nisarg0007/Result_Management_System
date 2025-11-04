

import sqlite3
import bcrypt
import maskpass
import re
import os
import shutil
from datetime import datetime
from cryptography.fernet import Fernet
from utils import log_event


# ===============================
# DATABASE CONNECTION
# ===============================
connection = sqlite3.connect("userdetails.db")
c = connection.cursor()

# ===============================
# TABLE CREATION
# ===============================
c.execute("""CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    roll_no TEXT UNIQUE,
    name TEXT,
    batch TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS teachers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    department TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS subjects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    credits INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
)""")

c.execute("""CREATE TABLE IF NOT EXISTS marks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    marks INTEGER NOT NULL,
    grade TEXT,
    grade_point REAL,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(subject_id) REFERENCES subjects(id),
    UNIQUE(student_id, subject_id, semester)
)""")

connection.commit()

# ===============================
# PASSWORD VALIDATION
# ===============================
def check_password_strength(password):
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number.")
    if not re.search(r"[@$!%*?&]", password):
        errors.append("Password must contain at least one special character (@$!%*?&).")
    return errors

# ===============================
# AUDIT LOG FUNCTION
# ===============================
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

# ===============================
# BACKUP & RECOVERY FUNCTION
# ===============================
def manage_backups():
    """Handles automatic/manual backups and restoration."""
    os.makedirs("backups", exist_ok=True)
    backup_dir = "backups"
    db_name = "userdetails.db"

    while True:
        print("\n=== Backup & Recovery Menu ===")
        print("1. Create manual backup")
        print("2. Restore from latest backup")
        print("3. List all backups")
        print("4. Return to main menu")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"userdetails_backup_{timestamp}.db")
            shutil.copy(db_name, backup_file)
            print(f"Backup created: {backup_file}")
            log_event("SYSTEM", "admin", f"Manual backup created: {backup_file}")

        elif choice == "2":
            backups = sorted(os.listdir(backup_dir))
            if not backups:
                print("No backups available.")
                continue
            latest = backups[-1]
            shutil.copy(os.path.join(backup_dir, latest), db_name)
            print(f"Database restored from: {latest}")
            log_event("SYSTEM", "admin", f"Database restored from {latest}")

        elif choice == "3":
            backups = sorted(os.listdir(backup_dir))
            if not backups:
                print("No backups found.")
            else:
                print("Available backups:")
                for b in backups:
                    print(" -", b)

        elif choice == "4":
            break
        else:
            print("Invalid option.")

# ===============================
# USER FUNCTIONS
# ===============================
def RegisterUser(role):
    table = "students" if role == "student" else "teachers"
    username = input(f"Enter {role} username: ").strip()
    if role == "student":
        roll_no = input("Enter roll number: ").strip()
        name = input("Enter student name: ").strip()
        batch = input("Enter batch (e.g. 2025): ").strip()
    else:
        name = input("Enter teacher name: ").strip()
        department = input("Enter department: ").strip()

    while True:
        password = maskpass.askpass(prompt="Enter new password: ", mask="•")
        errors = check_password_strength(password)
        if errors:
            print("Weak password:")
            for e in errors:
                print(" - " + e)
            print("Please try again.")
            continue

        confirm = maskpass.askpass(prompt="Confirm password: ", mask="•")
        if password != confirm:
            print("Passwords do not match. Try again.")
            continue
        break

    hashedpass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        if role == "student":
            c.execute("INSERT INTO students (username, password, roll_no, name, batch) VALUES (?, ?, ?, ?, ?)",
                      (username, hashedpass, roll_no, name, batch))
        else:
            c.execute("INSERT INTO teachers (username, password, name, department) VALUES (?, ?, ?, ?)",
                      (username, hashedpass, name, department))
        connection.commit()
        print("Registered successfully.")
        log_event(username, role, "Registered new account.")
    except sqlite3.IntegrityError:
        print("Username or roll number already exists.")
        choice = input("Do you want to [L]ogin or [T]ry again? (L/T): ").lower()
        if choice == "l":
            LoginUser(role)
        else:
            RegisterUser(role)

def LoginUser(role):
    table = "students" if role == "student" else "teachers"
    username = input(f"Enter {role} username: ").strip()
    password = maskpass.askpass(prompt="Enter password: ", mask="•")
    c.execute(f"SELECT id, password FROM {table} WHERE username = ?", (username,))
    result = c.fetchone()
    if result and bcrypt.checkpw(password.encode(), result[1]):
        user_id = result[0]
        print(f"{role.capitalize()} login successful.")
        log_event(username, role, "Logged in.")
        if role == "teacher":
            TeacherPortal(connection, user_id, username)
        else:
            StudentPortal(connection, user_id, username)
        log_event(username, role, "Logged out.")
    else:
        print("Invalid username or password.")
        log_event(username, role, "Failed login attempt.")

def ForgotPassword(role):
    table = "students" if role == "student" else "teachers"
    username = input(f"Enter your {role} username: ").strip()
    c.execute(f"SELECT id FROM {table} WHERE username = ?", (username,))
    result = c.fetchone()
    if not result:
        print("Username not found.")
        return
    while True:
        newpass = maskpass.askpass(prompt="Enter new password: ", mask="•")
        errors = check_password_strength(newpass)
        if errors:
            print("Weak password:")
            for e in errors:
                print(" - " + e)
            print("Try again.")
            continue
        confirm = maskpass.askpass(prompt="Confirm new password: ", mask="•")
        if newpass != confirm:
            print("Passwords do not match. Try again.")
            continue
        break
    hashedpass = bcrypt.hashpw(newpass.encode(), bcrypt.gensalt())
    c.execute(f"UPDATE {table} SET password=? WHERE username=?", (hashedpass, username))
    connection.commit()
    print("Password reset successful.")
    log_event(username, role, "Password reset.")

# ===============================
# MAIN MENU
# ===============================
from teacher_portal import TeacherPortal
from student_portal import StudentPortal

if __name__ == "__main__":
    while True:
        print("\nMAIN MENU")
        print("1. Register")
        print("2. Login")
        print("3. Forgot Password")
        print("4. Exit")
        print("5. Backup & Recovery")

        choice = input("Choose an option (1-5): ").strip()
        if choice in ["1", "2", "3"]:
            role = input("Are you a [student] or [teacher]? ").strip().lower()
            if role not in ["student", "teacher"]:
                print("Invalid role.")
                continue
            if choice == "1":
                RegisterUser(role)
            elif choice == "2":
                LoginUser(role)
            elif choice == "3":
                ForgotPassword(role)
        elif choice == "4":
            print("Goodbye.")
            break
        elif choice == "5":
            manage_backups()
        else:
            print("Invalid choice.")