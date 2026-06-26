# 🚀 Easy Tutorial: How Our Payroll App Works!

Imagine you are running a giant pizza shop. You have lots of workers, and you need a way to keep track of everyone, when they work, and how much money you need to pay them at the end of the month. That’s exactly what our app does!

Here is how the whole process works, step by step, explained so simply that anyone can understand it!

---

## 🍕 1. The Setup (Who's Who?)

Before anyone can start working, we need to set up the shop.
- **Company & Department:** We tell the app we have a company ("Pizza Planet") and it has different departments like "Kitchen" and "Delivery".
- **Employees:** We hire people and add them to the app. Each person gets a name, a role (like "Chef"), and a **Base Salary** (how much they earn).

## ⏰ 2. The Daily Routine (Punching In & Out)

When workers arrive at the shop, they need to tell the app they are there!
- **Punch In:** They press a button to say "I'm here!" The app looks at the time and creates a **Raw Attendance Log**. It's just a raw note of the exact time they clicked the button.
- **Punch Out:** When they go home, they press the button again.

## ⚙️ 3. The Magic Brain (Processing Attendance)

At the end of the day, a robot inside the app (the **Attendance Processing Service**) wakes up and looks at all the raw logs.
- It finds the first punch-in and the last punch-out for each worker.
- It calculates: *How many hours did they work?*
- If they worked extra hours, it counts as **Overtime**.
- If they missed a punch, came in late, or left early, the robot flags it as an **Anomaly** (a warning sign).
- The final result is saved in an **Attendance Record** for that day.

## 💰 4. Payday! (Calculating Payroll)

At the end of the month, it’s time to pay everyone! Another robot (the **Payroll Service**) gets to work.
- It gathers all the **Attendance Records** for the month.
- It checks the worker's **Base Salary**.
- **Earnings (Money In):** It adds money for regular days worked and extra money for overtime.
- **Deductions (Money Out):** It subtracts money for days the worker was absent or if they were severely late.
- It creates a **Payroll Entry** (a digital payslip) showing exactly how much they earned, how much was deducted, and their final **Net Pay**.

## 👁️ 5. Seeing the Results

- **The Dashboard:** The manager can open the app and see a beautiful screen showing how many people are working and how much the total payroll is.
- **Employee View:** Workers can log in and see their own daily attendance and check their digital payslips to see how much they got paid.

---

### 🎉 Summary of the Flow:
1. **Manager adds Employee.**
2. **Employee punches In and Out every day.**
3. **App turns punches into daily Attendance Records.**
4. **App uses Attendance Records to calculate monthly Pay (Payroll).**
5. **Everyone is happy!**

And that's it! Our app handles all the boring math and tracking so you can focus on making the best pizza in town! 🍕
