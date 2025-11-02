# **Result Management System🏫**  
*A Python-based console application developed by our team to manage student results efficiently, with separate portals for teachers and students.*  

---

## 📌 **About the Project**  
**Result Management System** is a collaborative Python project that implements CRUD operations (Create, Read, Update, Delete) to efficiently manage student results.

Our team designed this system using SQLite for secure and reliable data storage, and ReportLab to generate professional-looking PDF marksheets. It ensures that student records are stored safely and can be easily accessed, updated, or deleted whenever needed.

Note: This project was created as a part of a college team project, showcasing collaborative software development and Python database integration skills:  

---

## 🎯 **Key Features**

✅ **Teacher Portal**  
- Add new subjects with codes and credits.  
- Enter, update, or delete student marks.  
- View all student results (subject-wise).  
- View and sort student CGPAs (ascending/descending).  

✅ **Student Portal**  
- View semester-wise results in formatted tables.  
- Check SGPA and CGPA instantly.  
- Generate PDF marksheets with subject, marks, and grade details.  

✅ **PDF Generation**  
- Automatically creates a printable marksheet with course info, SGPA, and CGPA.

---

## 📌**Tech Stack**

| Technology | Purpose |
|-------------|----------|
| 🐍 **Python 3** | Core programming language |
| 🗄️ **SQLite3** | Database for storing marks, subjects & student details |
| 📄 **ReportLab** | PDF generation for marksheets |
| 📊 **Tabulate** | Beautifies console tables |
| 🔐 **bcrypt + maskpass** | Password encryption & secure login |

---


## 🚀 **Getting Started**
### **Run Locally**
```bash
# Clone the repository
git clone git@github.com:Nisarg0007/Result_Managament_System.git

# Navigate into the project folder
cd RESULT_MANAGEMENT_SYSTEM

# Install dependencies 
pip install -r requirements.txt

# Run the program
python main.py


```




