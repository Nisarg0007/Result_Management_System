import sqlite3
import bcrypt
import maskpass
import re
from teacher_portal import TeacherPortal
from student_portal import StudentPortal


connection = sqlite3.connect("userdetails.db")
c = connection.cursor()

# TABLES

#TABLE FOR STUDENT DATA
c.execute("""CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    roll_no TEXT UNIQUE,
    name TEXT,
    batch TEXT
)""")

#TEACHER DATA
c.execute("""CREATE TABLE IF NOT EXISTS teachers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    department TEXT
)""")

#SUBJECTS
c.execute("""CREATE TABLE IF NOT EXISTS subjects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    credits INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
)""")

#MARKS
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
    UNIQUE(student_id, subject_id, semester) -- prevent duplicates
)""")

connection.commit()

#PASSWORD STRENGTH CHECK, REGISTER, LOGIN, RESET PASSWORD
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
        if role == "teacher":
            TeacherPortal(connection, user_id, username)
        else:
            StudentPortal(connection, user_id, username)
    else:
        print("Invalid username or password.")


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


if __name__ == "__main__":
    while True:
        print("\nMAIN MENU")
        print("1. Register")
        print("2. Login")
        print("3. Forgot Password")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()
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
        else:
            print("Invalid choice.")
