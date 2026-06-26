# 🧩 Database Models Explained (The Simple Way!)

Think of a database like a massive filing cabinet with different folders (Models). Each folder holds specific types of documents. Some documents have sticky notes pointing to other documents. Let's look inside our cabinet!

## 🏢 1. The Foundation (Company & Department)
Before we hire anyone, we need a place for them to work.
*   **Company:** Just the name of the business (e.g., "Tech Innovators").
*   **Department:** A section of the company (e.g., "Engineering", "Sales"). *Points to a Company.*

## 👤 2. The People (Employee)
*   **Employee:** The core of our app! It holds the worker's name, email, and base salary.
    *   *Points to a Company and a Department.*
    *   It also connects to Django's built-in `User` model, which holds their password and lets them log into the app.

## ⏰ 3. Time Tracking (Shifts & Punches)
*   **Shift:** The expected working hours (e.g., 9 AM to 5 PM).
*   **Shift Assignment:** Connects an Employee to a specific Shift.
*   **RawAttendanceLog:** Every single time an employee presses the "Punch" button, it creates one of these. It just records "Who", "When", and "Where". *Points to the Employee.*
*   **AttendanceRecord:** At the end of the day, all the raw punches are combined into one neat summary for the day. It shows "Time In", "Time Out", "Total Hours", "Overtime", and "Status" (Present/Absent). *Points to the Employee.*

## 🏖️ 4. Time Off (Leaves)
*   **LeaveType:** Kinds of time off (e.g., "Sick Leave", "Vacation").
*   **LeaveBalance:** How many days off an employee has left. *Points to Employee and LeaveType.*
*   **LeaveRequest:** When an employee asks for time off. A manager can approve or reject it. *Points to Employee and LeaveType.*

## 💸 5. Money Matters (Payroll)
*   **PayrollPeriod:** A specific chunk of time for getting paid (e.g., "May 2026").
*   **PayrollRun:** A batch process where the manager says "Calculate everyone's pay for May 2026!" *Points to PayrollPeriod.*
*   **PayrollEntry:** The actual "Payslip" for a single employee for that period. It stores their gross earnings, deductions, and final net pay. *Points to Employee and PayrollRun.*

## 🕵️ 6. The Tracker (AuditLog)
*   **AuditLog:** The security camera of the app. Every time someone creates, edits, or deletes any record, the AuditLog writes it down. It keeps track of "Who did it", "What did they do", and "When did they do it".

---

### 🔗 How They Connect (The Big Picture)

If you look closely, almost everything points back to the **Employee**!

1. An **Employee** belongs to a **Company/Department**.
2. An **Employee** punches the clock, creating **RawAttendanceLogs**.
3. Those logs become a daily **AttendanceRecord** for the **Employee**.
4. The app looks at all **AttendanceRecords** to create a **PayrollEntry** (payslip) for the **Employee**.

It’s all connected in a neat web that automates the whole payroll process!
