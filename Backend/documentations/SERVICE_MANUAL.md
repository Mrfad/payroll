# Payroll Application Service Manual

This comprehensive guide covers everything you need to know about setting up, running, testing, and maintaining the Django-based Payroll application.

---

## 1. Environment Setup

Ensure you are using Python 3.10+ (tested on Python 3.14).

### Creating a Virtual Environment
It's highly recommended to use a virtual environment to isolate the project dependencies:
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows:** `.\venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### Installing Dependencies
Install all required packages from `requirements.txt`. Note that the application uses Django REST Framework, Django Channels (for websockets), SimpleJWT, and PostgreSQL/SQLite compatibility libraries.
```bash
pip install -r requirements.txt
```

*(Note: Depending on your exact testing environment, you might also need `pytest`, `pytest-django`, `pytest-cov`, `pytest-mock`, and `pytest-asyncio` installed).*

---

## 2. Database Management

The project is currently configured to use a local `db.sqlite3` file by default (or PostgreSQL if configured in your environment).

### Applying Migrations
Before running the app or tests, make sure your database schema is up-to-date:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating an Admin User
You'll need a superuser account to access the Django Admin panel or perform administrative API requests:
```bash
python manage.py createsuperuser
```

---

## 3. Running the Application

Because this application uses **Django Channels** for WebSockets (noted by the presence of `daphne` and `consumers.py`), it is recommended to run the app using Daphne or ASGI in production. However, for local development, `runserver` will automatically hook into the channels development server.

```bash
python manage.py runserver
```
The application will be available at `http://127.0.0.1:8000/`.

---

## 4. Running the Test Suite

The project uses `pytest` configured through `pytest.ini`. The testing suite checks standard views, authentication, WebSockets, and the custom device endpoints.

### 1. Run Tests for Employees & Core Payroll Only
If you want to run tests exclusively for the `payroll` app (which handles employees, attendance, and core dashboard logic):
```bash
pytest payroll/tests/
```

### 2. Run Tests for Devices Only
If you want to run tests exclusively for the `device` app (which handles device configurations, tokens, and the push API):
```bash
pytest device/tests.py
```

### 3. Run a Complete Test for Everything
To run every test in the entire project across all apps:
```bash
pytest
```

### Run Everything with Coverage
To see test coverage across the entire project (useful for identifying untested files and logic branches):
```bash
pytest --cov=.
```

---

## 5. Helpful Management Commands

The application includes several custom scripts designed to make testing and administration easier.

### 1. `emulate_device`
**Purpose:** Simulates physical attendance machines sending bulk punch data to the server. Useful for load testing and verifying the `/push/` API endpoint.
**Usage:**
```bash
python manage.py emulate_device --count 20
```
*Note: This command will automatically identify active employees and simulate 20 random attendance punches.*

### 2. `generate_sample_data`
**Purpose:** Seeds the database with random company, department, and employee data to give you a sandbox environment.
**Usage:**
```bash
python manage.py generate_sample_data
```

### 3. `cleanup_deleted_employees`
**Purpose:** The application uses "soft deletes" (marking employees with `deleted_at`). This script permanently cleans up these soft-deleted records from the database.
**Usage:**
```bash
python manage.py cleanup_deleted_employees
```

---

## 6. Architecture & Security Notes

### Authentication Concepts
1. **Human Users (Dashboard/Mobile App):** 
   - Uses **JWT Authentication** (`djangorestframework_simplejwt`). 
   - Endpoints: `/api/v1/token/` (login), `/api/v1/token/refresh/`, `/api/v1/token/verify/`.
   - Headers: `Authorization: Bearer <token>`
2. **Physical Devices (Attendance Machines):**
   - Uses custom **DeviceTokenAuthentication**.
   - Authenticates using an auto-generated `api_token` belonging to a `DeviceConfiguration`.
   - Headers: `X-Device-Token: <UUID>`

### WebSockets
Real-time events (like broadcasting attendance punches) are handled via Django Channels. If deploying to production, remember to configure a channel layer backend like Redis.
