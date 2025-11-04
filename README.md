# **Result Management System🏫**  
*A Python-based console application developed by our team to manage student results efficiently, with separate portals for teachers and students.*  

---

## 📌 **About the Project**  
**Result Management System** is a collaborative Python project that implements CRUD operations (Create, Read, Update, Delete) to efficiently manage student results.

The system is built using **SQLite** for secure and reliable data storage, and **ReportLab** for generating professional PDF marksheets.  
It now includes **modular code improvements** (`utils.py`), **audit log tracking** (`view_audit_logs.py`), and enhanced **user authentication** for both students and teachers.

> 🧠 This project was created as part of a college software development course, focusing on teamwork, modular design, and real-world database integration.

---

## 🎯 **Key Features**

✅ **Teacher Portal**  
- Add new subjects with codes and credits.  
- Enter, update, or delete student marks.  
- View all student results (subject-wise).  
- View and sort student CGPAs (ascending/descending).  
- Manage audit logs (track who updated which record).  

✅ **Student Portal**  
- View semester-wise results in formatted tables.  
- Instantly view SGPA and CGPA.  
- Download PDF marksheets with subject, marks, and grade details.  
- Secure login using encrypted passwords.  

✅ **Audit Log System**  
- Added in the latest update (`view_audit_logs.py`).  
- Records all important actions (like data edits or deletions) for transparency.  
- Viewable only by authorized users.  

✅ **Utility Module (`utils.py`)**  
- Centralized helper functions for cleaner code.  
- Handles repetitive tasks like grade calculations, validation, and formatting.

✅ **PDF Generation**  
- Automatically creates printable marksheets using ReportLab.  
- Includes student name, course details, SGPA, and CGPA.  

---

## 📌 **Tech Stack**

| Technology | Purpose |
|-------------|----------|
| 🐍 **Python 3** | Core programming language |
| 🗄️ **SQLite3** | Database for storing marks, subjects & student details |
| 📄 **ReportLab** | PDF generation for marksheets |
| 📊 **Tabulate** | Beautifies console tables |
| 🔐 **bcrypt + maskpass** | Password encryption & secure login |
| 🧩 **Custom Utility Scripts** | Code reusability and modularization |

---

## 🚀 **Getting Started**

### **Run Locally**
```bash
# Clone the repository
git clone https://github.com/Nisarg0007/Result_Managament_System.git

# Navigate into the project folder
cd RESULT_MANAGEMENT_SYSTEM

# Install dependencies 
pip install -r requirements.txt

# Run the program
python main.py


