# Unit Testing Guide

Welcome to the testing guide! Because our system is split into multiple independent applications (Domain-Driven Design), our test suite is also decoupled. This makes it easier to test specific features without having to run everything at once.

## 🗂️ Test Structure

Each app has its own `tests/` directory containing all the unit tests for its specific domain:

- `employees/tests/`: Tests for users, companies, departments, permissions, and core signals.
- `attendance/tests/`: Tests for time tracking, shifts, breaks, overtime, and leave management.
- `payroll/tests/`: Tests for salary calculations, payslips, and payroll generation commands.
- `device/tests.py`: Tests for external clock devices pushing raw punches via API.

## 🚀 How to Run Tests

### 1. Run Everything (Full Suite)
If you want to make sure everything in the entire project works perfectly:
```bash
pytest
```
*(You can also use `pytest -v` for more detailed "verbose" output).*

### 2. Test a Specific App (Fastest)
If you are only making changes to the `attendance` app, you don't need to run payroll tests. Test just the attendance module:
```bash
pytest attendance/tests/
```

### 3. Test a Specific File
If you are debugging a specific file (e.g., test models in employees):
```bash
pytest employees/tests/test_models.py
```

### 4. Test a Specific Function
If you only want to run one specific test by name:
```bash
pytest employees/tests/test_models.py::TestEmployeeModel::test_employee_string_representation
```

---

## 🛠️ Dealing with Database Issues

By default, Pytest creates a brand new database called `test_deskshieldpayroll` every time it runs, and deletes it when it's done.

### The `--reuse-db` Flag
Creating the database takes time. If you are running tests over and over, tell Pytest to keep the database alive and reuse it!
```bash
pytest --reuse-db
```
*Note: If the test database gets "stuck" or encounters a `DuplicateDatabase` error, simply run `pytest --create-db` or press `yes` if Pytest asks to drop the old one.*

---

## 🧪 Libraries We Use

- **`pytest`**: The main test runner. Much easier to read than standard Django tests.
- **`pytest-django`**: Helps Pytest understand our Django database and settings.
- **`pytest-asyncio`**: Allows us to test asynchronous code (like WebSockets).
- **`pytest-mock`**: Allows us to "mock" (fake) certain functions. For example, faking the `process_attendance` command when running payroll tests so we don't accidentally write to the database twice.

## 📝 Writing New Tests

1. **Where to put them**: Inside the relevant app's `tests/` folder.
2. **File Naming**: The file must start with `test_` (e.g., `test_salary.py`).
3. **Function Naming**: The test function must start with `test_` (e.g., `def test_calculate_bonus():`).
4. **Fixtures**: Use the shared dummy data (like dummy users and companies) provided in `conftest.py` inside the root backend folder.

Happy Testing! 🚀
