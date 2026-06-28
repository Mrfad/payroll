# Payroll Backend System

This Django project has been refactored from a monolithic app into a Domain-Driven modular architecture consisting of 7 distinct applications. This modularization separates concerns, enhances testability, and enables distinct teams to work on independent modules.

## Architectural Structure

The project is split into the following apps:

1. **`employees`** (Core)
   - Handles identities, companies, departments, user profiles, and audit logging.
   - Core API endpoints: `/api/v1/employees/`
2. **`attendance`**
   - Manages time tracking, shifts, breaks, overtimes, and leave management.
   - Core API endpoints: `/api/v1/attendance/`
3. **`payroll`**
   - Handles compensation logic, salary components, and payroll calculations.
   - Core API endpoints: `/api/v1/payroll/`
4. **`recruitment`** (Scaffolded)
   - Future application to handle job postings, candidates, and hiring workflows.
5. **`assets`** (Scaffolded)
   - Future application to manage physical or digital equipment assigned to employees.
6. **`performance`** (Scaffolded)
   - Future application for evaluations, OKRs, and KPIs tracking.
7. **`helpdesk`** (Scaffolded)
   - Future application for internal IT/HR ticketing.

*(There is also a legacy `device` app for handling hardware clock integrations).*

## Testing

The test suite has been split along domain boundaries, so you no longer need to run a massive, monolithic test suite.

You can test individual apps independently using pytest:
```bash
pytest employees/tests/
pytest attendance/tests/
pytest payroll/tests/
```

*Note: If test databases get stuck, you can append `--reuse-db` to speed up subsequent runs or drop the existing test databases.*

## Automatic Migrations

All models map to their original `db_table` schemas. When models were moved between apps (e.g., `Employee` moving to `employees`), their original table structures were preserved. No database data is dropped when migrating between the old structure and the new domain-driven structure.

## Services & Commands

- **Attendance Processing**: `python manage.py process_attendance` (Located in `attendance/management/commands/`)
- **Run Payroll**: `python manage.py run_payroll` (Located in `payroll/management/commands/`)
- **Cleanup Employees**: `python manage.py cleanup_deleted_employees` (Located in `employees/management/commands/`)

## WebSockets
WebSocket connections (`/ws/updates/`) are managed by the `employees` app via `consumers.py` and `routing.py`. When core data entities update, signals broadcast live changes to connected clients automatically.
