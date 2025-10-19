from tabulate import tabulate

def calculate_grade(marks):
    if marks >= 90:
        return "S", 10.0
    if marks >= 80:
        return "A", 9.0
    if marks >= 70:
        return "B", 8.0
    if marks >= 60:
        return "C", 7.0
    if marks >= 50:
        return "D", 6.0
    if marks >= 40:
        return "E", 5.0
    return "F", 0.0


def compute_cgpa_for_student(conn, student_id):
    c = conn.cursor()
    c.execute("""
        SELECT m.grade_point, s.credits
        FROM marks m
        JOIN subjects s ON m.subject_id = s.id
        WHERE m.student_id = ?
    """, (student_id,))
    rows = c.fetchall()
    total_points = 0
    total_credits = 0
    for gp, cr in rows:
        total_points += (gp or 0) * cr
        total_credits += cr
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)


def TeacherPortal(connection, teacher_id, username):
    c = connection.cursor()
    print(f"Welcome, {username}. Teacher Portal")

    while True:
        print("\nTeacher Menu")
        print("1. Add subject")
        print("2. Enter result")
        print("3. Update result")
        print("4. Delete result")
        print("5. View all my results")
        print("6. View class list (with CGPA)")
        print("7. Logout")
        choice = input("Choose an option: ").strip()

        # ADDING COURSE
        if choice == "1":
            code = input("Subject code: ").strip()
            name = input("Subject name: ").strip()
            credits = int(input("Credits: ").strip())
            try:
                c.execute(
                    "INSERT INTO subjects (code, name, credits, teacher_id) VALUES (?, ?, ?, ?)",
                    (code, name, credits, teacher_id)
                )
                connection.commit()
                print("Subject added.")
            except Exception as e:
                print("Error:", e)

        #ENTER RESULT
        elif choice == "2":
            #STUDENT LIST
            c.execute("SELECT id, username, roll_no, name FROM students")
            students = c.fetchall()
            print(tabulate(students, headers=["id", "username", "roll_no", "name"], tablefmt="grid"))
            student_username = input("Enter student username: ").strip()
            c.execute("SELECT id, name FROM students WHERE username=?", (student_username,))
            student = c.fetchone()
            if not student:
                print("Student not found.")
                continue
            student_id = student[0]

            #TEACHER'S SUBJECTS
            c.execute("SELECT id, code, name, credits FROM subjects WHERE teacher_id=?", (teacher_id,))
            subjects = c.fetchall()
            if not subjects:
                print("No subjects. Add subjects first.")
                continue
            print(tabulate(subjects, headers=["id", "code", "name", "credits"], tablefmt="grid"))
            subject_id = int(input("Enter subject id: ").strip())
            semester = int(input("Semester number: ").strip())

            #AVOIDING DUPLICATES
            c.execute("SELECT id FROM marks WHERE student_id=? AND subject_id=? AND semester=?",
                      (student_id, subject_id, semester))
            if c.fetchone():
                print("Marks already entered. Use update option instead.")
                continue

            marks = int(input("Marks (0-100): ").strip())
            grade, gp = calculate_grade(marks)
            c.execute(
                "INSERT INTO marks (student_id, subject_id, semester, marks, grade, grade_point) VALUES (?, ?, ?, ?, ?, ?)",
                (student_id, subject_id, semester, marks, grade, gp)
            )
            connection.commit()
            print("Result recorded.")

            #UPDATE RESULT
        elif choice == "3":
            student_username = input("Enter student username: ").strip()
            c.execute("SELECT id FROM students WHERE username=?", (student_username,))
            student = c.fetchone()
            if not student:
                print("Student not found.")
                continue
            student_id = student[0]

            c.execute("SELECT id, code, name FROM subjects WHERE teacher_id=?", (teacher_id,))
            subjects = c.fetchall()
            if not subjects:
                print("You have no subjects.")
                continue
            print(tabulate(subjects, headers=["id", "code", "name"], tablefmt="grid"))
            subject_id = int(input("Enter subject id: ").strip())
            semester = int(input("Semester number: ").strip())

            c.execute("SELECT id FROM marks WHERE student_id=? AND subject_id=? AND semester=?",
                      (student_id, subject_id, semester))
            mark_row = c.fetchone()
            if not mark_row:
                print("No existing result. Use Add Result option.")
                continue

            marks = int(input("New marks: ").strip())
            grade, gp = calculate_grade(marks)
            c.execute("UPDATE marks SET marks=?, grade=?, grade_point=? WHERE student_id=? AND subject_id=? AND semester=?",
                      (marks, grade, gp, student_id, subject_id, semester))
            connection.commit()
            print("Result updated.")

        #DELETE REAULT
        elif choice == "4":
            student_username = input("Enter student username: ").strip()
            c.execute("SELECT id FROM students WHERE username=?", (student_username,))
            student = c.fetchone()
            if not student:
                print("Student not found.")
                continue
            student_id = student[0]

            c.execute("SELECT id, code, name FROM subjects WHERE teacher_id=?", (teacher_id,))
            subjects = c.fetchall()
            if not subjects:
                print("You have no subjects.")
                continue
            print(tabulate(subjects, headers=["id", "code", "name"], tablefmt="grid"))
            subject_id = int(input("Enter subject id: ").strip())
            semester = int(input("Semester number: ").strip())

            c.execute("DELETE FROM marks WHERE student_id=? AND subject_id=? AND semester=?",
                      (student_id, subject_id, semester))
            connection.commit()
            print("Result deleted...")

        #VIEW ALL RESULT
        elif choice == "5":
            c.execute("""SELECT s.username, s.roll_no, s.name, subj.code, subj.name, m.semester, m.marks, m.grade
                         FROM marks m
                         JOIN students s ON m.student_id = s.id
                         JOIN subjects subj ON m.subject_id = subj.id
                         WHERE subj.teacher_id=?
                         ORDER BY s.username, m.semester""", (teacher_id,))
            rows = c.fetchall()
            if rows:
                print(tabulate(rows, headers=["username", "roll_no", "name", "subj_code", "subject", "sem", "marks", "grade"], tablefmt="grid"))
            else:
                print("No results found.")

        #VIEW CLASS LIST AND SORT BASED ON CGPA
        elif choice == "6":
            from operator import itemgetter

            c.execute("SELECT id, username, name, roll_no FROM students")
            students = c.fetchall()
            class_list = []
            for s in students:
                sid, uname, sname, roll_no = s
                cgpa = compute_cgpa_for_student(connection, sid)
                class_list.append((sid, uname, roll_no, sname, cgpa))

            if not class_list:
                print("No students.")
                continue

            order = input("Sort by CGPA? [desc/asc/none]: ").strip().lower()
            if order == "desc":
                class_list = sorted(class_list, key=itemgetter(4), reverse=True)
            elif order == "asc":
                class_list = sorted(class_list, key=itemgetter(4))

            print(tabulate(class_list, headers=["student_id", "username", "roll_no", "name", "CGPA"], tablefmt="grid"))


        
        elif choice == "7":
            print("Logging out.")
            break

        else:
            print("Invalid choice.")
