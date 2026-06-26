# 🚀 How Our Awesome Payroll App Works! (The Easy Guide)

Welcome to the big picture! Imagine you are building a giant Lego city. To make the city run, you need people, places to work, machines to track time, and a way to pay everyone at the end of the month!

Our app does exactly that. Let’s break it down so easily that anyone can understand it!

---

## 🏗️ The 3 Main Pieces of Our App

Our app is built in three different pieces that all talk to each other:

1. **The Brain (Django Backend)**: This is the main server. It lives in the `Backend` folder. It holds all the databases, does all the hard math, and remembers everything.
2. **The Website (React WebApp)**: This is what managers see when they log in from their internet browser. It lives in the `WebApp` folder.
3. **The Phone & Computer App (Flutter ClientApp)**: This is the app you can install on your iPhone, Android, or Windows computer. It lives in the `ClientApp` folder.

Whenever the Website or Phone App needs to know something, they send a quick text message (called an **API Request**) to the Brain!

---

## 🏢 How Our Database Models Work Together

Think of "Models" as boxes where we store information. Here is how they stack together:

### 1. The Big Boss Box: `Company` 🏢
Everything starts here. You can't have employees without a company! 

### 2. The Rooms: `Department` 🚪
Inside the Company, we have different rooms (like "Sales" or "Engineering"). Every Department belongs to a Company.

### 3. The People: `Employee` 👨‍💻
Every Employee belongs to a **Department**. The Employee box holds their name, their ID, and their job title.

---

## ⏰ The Time Tracking Journey (Step-by-Step)

How does a person actually punch in, and how does the brain know?

### Step 1: The Machine (`DeviceConfiguration`) 📷
We put a machine on the wall (like a fingerprint scanner or a face scanner). In our database, this is called a `DeviceConfiguration`. The brain needs to know this machine exists so it can trust it!

### Step 2: The Raw Punch (`RawAttendanceLog`) 👊
When an employee scans their finger, the machine sends a quick message to the Brain: *"Hey! ID #123 just scanned at 9:00 AM!"*
The Brain saves this exact message in a box called the `RawAttendanceLog`. It's "raw" because it hasn't been processed yet.

### Step 3: Making Sense of it (`AttendanceRecord`) 📅
The Brain looks at the `RawAttendanceLog` and says:
- *"Who is ID #123? Oh, that's John!"*
- *"He punched in at 9:00 AM and punched out at 5:00 PM."*
- *"That means he worked for 8 hours today!"*

The Brain takes all this math and creates a neat, finished **`AttendanceRecord`** for John for that specific day. It marks him as "Present".

*(If the machine says someone punched in, but the Brain doesn't know who they are, our **Auto-Enrollment** magic creates a new Employee account for them instantly!)*

---

## 💰 Getting Paid (`PayrollEntry`)

At the end of the month, John wants his money!

1. The Brain gathers all of John's `AttendanceRecord`s for the month.
2. It adds up all his total hours and any overtime he did.
3. It creates a **`PayrollEntry`** (a Payslip).
4. This Payslip calculates his Gross Pay (total money earned) minus any Deductions (taxes, late penalties) to give him his **Net Pay** (the money he actually takes home).

---

## ⚡ The Real-Time Magic (WebSockets)

What happens if a manager is looking at the Website, and John punches in on the wall machine? Does the manager have to click "Refresh"?

**NO!** 🪄

We use something called **WebSockets**. Think of WebSockets like a live walkie-talkie connection.
When John punches in, the Brain calculates his `AttendanceRecord` and instantly shouts into the walkie-talkie: *"HEY EVERYONE! JOHN JUST PUNCHED IN!"*

Both the Website and the Phone App hear this shout and instantly update their screens right in front of your eyes!

---

## 🎯 Summary Flow

1. You create a **Company** and **Department**.
2. An **Employee** is hired.
3. They scan their finger on a **Device**.
4. The device sends a **Raw Log** to the Brain.
5. The Brain turns it into an **Attendance Record**.
6. At the end of the month, it turns into a **Payslip**.
7. Everybody is happy! 🎉
