# 🎮 The Super Easy Guide to Fake Attendance Machines!

Welcome! If you want to pretend that employees are scanning their faces or fingerprints to go to work, you are in the right place!

We are going to use **Simulators**. A simulator is just a computer program that *pretends* to be a physical machine on the wall.

Follow these 3 simple steps to make the magic happen!

---

## Step 1: Turn on the Main Server 🔌
Before our fake machines can talk, the main brain (the server) needs to be awake.

1. Open your terminal (or command prompt).
2. Go into the `Backend` folder.
3. Type this command and press Enter:
   ```bash
   python manage.py runserver
   ```
*Leave this window open! Your server is now listening for punches.*

---

## Step 2: Plug in the Fake Machines 🧩
Now we need to tell the server, *"Hey! We are adding some fake machines!"*

1. Open a **New** terminal window (keep the first one running).
2. Make sure you are inside the `Backend` folder.
3. Type this magic spell and press Enter:
   ```bash
   python manage.py setup_env
   ```

**What just happened?**
The system just created 7 pretend machines in the database (like a pretend Hikvision or ZKTeco machine). They are plugged in and ready to go!

---

## Step 3: Punch In! ⏰
Now for the fun part! Let's make an employee punch in for work.

1. In that same new terminal window, go back to the main project folder (the folder that has the `simulators` folder in it).
2. Type this command and press Enter:
   ```bash
   python simulators/simulate.py hikvision FADY-001
   ```

### 🎩 The Magic Trick (Auto-Enrollment!)
Wait, who is `FADY-001`? We never created them!
Don't worry! Because of a super smart feature called **Auto-Enrollment**:
1. The fake Hikvision machine sends a message: *"FADY-001 just punched in!"*
2. The server looks for `FADY-001` and says: *"I don't know who that is, but I'll create an account for them right now!"*
3. The server instantly creates a new Employee named `FADY-001`, assigns them to an "Unassigned" department, and records their punch.

---

## Want to see it working? 👀
1. Go to your Web App or Desktop App.
2. Click on the **Employees** list.
3. You will see a brand new employee named **FADY-001**!
4. Click on their name, go to the **Attendance** tab, and you will see the exact time they just punched in!

## Extra Fun Commands 🎈

**Want to punch OUT?**
```bash
python simulators/simulate.py hikvision FADY-001 --direction out
```

**Want to make 3 people punch in at the same time?**
```bash
python simulators/simulate.py zkteco EMP001,EMP002,EMP003
```

**Want the machine to keep punching in and out forever automatically? (Interactive Mode)**
```bash
python simulators/simulate.py suprema FADY-001 --interactive
```
*(Press `Ctrl + C` on your keyboard to stop it!)*

**Want to generate 5 days of history for someone?**
```bash
python simulators/simulate.py dahua FADY-001 --batch --days 5
```

---
**And that's it! You are now a master of pretend attendance machines!** 🎉
