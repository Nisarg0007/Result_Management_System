from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from utils import log_event


def calculate_sgpa(conn, student_id, semester):
    c = conn.cursor()
    c.execute("""
        SELECT m.grade_point, s.credits
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        WHERE m.student_id=? AND m.semester=?
    """, (student_id, semester))
    data = c.fetchall()
    total_points = 0
    total_credits = 0
    for gp, cr in data:
        total_points += (gp or 0) * cr
        total_credits += cr
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)

def calculate_cgpa(conn, student_id):
    c = conn.cursor()
    c.execute("""
        SELECT m.grade_point, s.credits
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        WHERE m.student_id=?
    """, (student_id,))
    data = c.fetchall()
    total_points = 0
    total_credits = 0
    for gp, cr in data:
        total_points += (gp or 0) * cr
        total_credits += cr
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)

def generate_marksheet_pdf(conn, student_id, username, semester):
    c = conn.cursor()
    c.execute("SELECT roll_no, name, batch FROM students WHERE id=?", (student_id,))
    info = c.fetchone()
    if not info:
        print("Student info missing.")
        return
    roll_no, name, batch = info
    c.execute("""
        SELECT subj.code, subj.name, subj.credits, m.marks, m.grade
        FROM marks m
        JOIN subjects subj ON m.subject_id = subj.id
        WHERE m.student_id=? AND m.semester=?
    """, (student_id, semester))
    rows = c.fetchall()
    sgpa = calculate_sgpa(conn, student_id, semester)
    cgpa = calculate_cgpa(conn, student_id)
    filename = f"{username}_sem{semester}_marksheet.pdf"
    pdf = canvas.Canvas(filename, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(180, 750, "VIT Vellore - Marksheet")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, 720, f"Name: {name}")
    pdf.drawString(300, 720, f"Roll No: {roll_no}")
    pdf.drawString(50, 700, f"Batch: {batch}")
    pdf.drawString(300, 700, f"Semester: {semester}")
    y = 670
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Code")
    pdf.drawString(120, y, "Subject")
    pdf.drawString(320, y, "Credits")
    pdf.drawString(380, y, "Marks")
    pdf.drawString(430, y, "Grade")
    pdf.setFont("Helvetica", 10)
    for r in rows:
        y -= 18
        pdf.drawString(50, y, str(r[0]))
        pdf.drawString(120, y, str(r[1])[:40])
        pdf.drawString(320, y, str(r[2]))
        pdf.drawString(380, y, str(r[3]))
        pdf.drawString(430, y, str(r[4]))
        if y < 80:
            pdf.showPage()
            y = 750
    y -= 30
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, f"SGPA: {sgpa}")
    pdf.drawString(200, y, f"CGPA: {cgpa}")
    pdf.save()
    print("📄 Marksheet saved as", filename)
    log_event(username, "student", f"Downloaded marksheet PDF for semester {semester}.")

def StudentPortal(connection, student_id, username):
    c = connection.cursor()
    print(f"Welcome, {username}. Student Portal")

    while True:
        print("\nStudent Menu")
        print("1. View my results (semester)")
        print("2. View consolidated CGPA")
        print("3. Download marksheet (PDF)")
        print("4. Logout")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            semester = int(input("Enter semester number: ").strip())
            c.execute("""
                SELECT subj.code, subj.name, subj.credits, m.marks, m.grade
                FROM marks m
                JOIN subjects subj ON m.subject_id = subj.id
                WHERE m.student_id=? AND m.semester=?
            """, (student_id, semester))
            rows = c.fetchall()
            if not rows:
                print("No results found for this semester.")
                continue
            headers = ["Code", "Subject", "Credits", "Marks", "Grade"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            sgpa = calculate_sgpa(connection, student_id, semester)
            cgpa = calculate_cgpa(connection, student_id)
            print(f"SGPA: {sgpa}   CGPA: {cgpa}")
            log_event(username, "student", f"Viewed results for semester {semester}.")

        elif choice == "2":
            cgpa = calculate_cgpa(connection, student_id)
            print("Your CGPA is:", cgpa)
            log_event(username, "student", "Viewed consolidated CGPA.")

        elif choice == "3":
            semester = int(input("Enter semester for marksheet: ").strip())
            generate_marksheet_pdf(connection, student_id, username, semester)

        elif choice == "4":
            print("Logging out.")
            log_event(username, "student", "Logged out of portal.")
            break

        else:
            print("Invalid choice.")