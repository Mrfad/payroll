# Unit Testing Documentation

## Architecture After Domain Decomposition

Our platform has been refactored from a monolithic `payroll` app into distinct bounded domains (Phase 2). As a result, the tests have been successfully distributed to their respective apps to ensure true modularity.

## Where are the tests located?
The unit tests are now organized directly within their respective domain folders:

- `accounts/tests/`: Authentication, users, roles, and API access tests.
- `companies/tests/`: Tenants, branches, and departments tests.
- `employees/tests/`: Core employee logic and profiles tests.
- `attendance/tests/`: Shifts, leave types, attendace recording, and calculation tests.
- `audit/tests/`: Action logging and audit trail tests.
- `device/tests.py`: Biometric device configuration and webhook tests.
- `payroll/tests/`: Core salary processing, compensation, and calculations tests.

## How to Run Tests
We use `pytest` as our testing framework. You can run the entire test suite from the `Backend` directory using the following command:

```bash
pytest -v --nomigrations --reuse-db
```

*Note: The `--nomigrations` flag skips running the database migrations during test setup, which significantly speeds up test execution and prevents migration-related errors. The `--reuse-db` flag preserves the test database across runs, preventing errors related to database locks and speeding up consecutive test runs.*

## Writing a New Test
If you want to add a new test, locate the appropriate test file within the correct domain (or create a new one) and add a method starting with `test_`. 
For example, to add an employee test in `employees/tests/test_models.py`:

```python
import pytest
from employees.models import Employee

@pytest.mark.django_db
def test_employee_creation():
    employee = Employee.objects.create(...)
    assert employee is not None
```

## Troubleshooting
If you encounter `AssertionError: assert not self._finalizers`, ensure you are not mixing `django_db` markers with improper database setup, and use `--reuse-db` as recommended above.
