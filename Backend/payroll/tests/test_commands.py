# Backend\payroll\tests\test_commands.py
import uuid
from io import StringIO
from unittest.mock import patch

import pytest
from attendance.models import AttendanceRecord
from companies.models import Company
from device.models import DeviceConfiguration
from django.contrib.auth.models import User
from django.core.management import call_command
from employees.models import Employee

from payroll.models import PayrollRun


@pytest.fixture
def base_data():
    user = User.objects.create(username="testuser")
    company = Company.objects.create(name="Test Company")
    employee = Employee.objects.create(
        user=user,
        company=company,
        employee_id="EMP123",
        device_user_ids={"zkteco": "EMP123"},
    )
    device = DeviceConfiguration.objects.create(
        company=company, name="Main Door", device_type="zkteco", api_token=uuid.uuid4()
    )

    return {"company": company, "employee": employee, "device": device}


@pytest.mark.django_db
class TestManagementCommands:
    def test_install_command(self):
        # Ensure clean state
        DeviceConfiguration.objects.all().delete()
        Company.objects.all().delete()
        User.objects.all().delete()

        out = StringIO()
        # use interact=False if the command expects inputs, but install prompts using input().
        # We might need to mock input, or test the non-interactive part.
        # Wait, let's mock input to return 'n' (no dummy users)
        from unittest.mock import patch

        with patch("builtins.input", return_value="n"):
            call_command("install", stdout=out)

        output = out.getvalue()

        assert "Setup Complete!" in output
        assert Company.objects.count() == 1
        assert DeviceConfiguration.objects.count() == 7
        assert User.objects.filter(is_superuser=True).count() == 1

    @patch("attendance.services.AttendanceProcessingService.process_pending_logs")
    def test_process_attendance_command(self, mock_process):
        mock_process.return_value = (5, 0)
        out = StringIO()
        call_command("process_attendance", stdout=out)
        assert "Successfully processed 5 logs." in out.getvalue()
        mock_process.assert_called_once()

    @patch(
        "payroll.management.commands.run_payroll.PayrollCalculationService.calculate_payroll"
    )
    def test_run_payroll_command(self, mock_calc, base_data):
        from datetime import date

        from payroll.models import PayrollPeriod

        period = PayrollPeriod.objects.create(
            company=base_data["company"],
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            status="draft",
        )

        class MockRun:
            id = 99

        mock_calc.return_value = MockRun()

        out = StringIO()
        call_command("run_payroll", period.id, stdout=out)
        assert f"Successfully calculated payroll. Run ID: 99" in out.getvalue()
        mock_calc.assert_called_once_with(period.id)

    def test_cleanup_deleted_employees_command(self, base_data):
        from datetime import timedelta

        from django.utils import timezone

        emp = base_data["employee"]
        emp.deleted_at = timezone.now() - timedelta(days=40)
        emp.save()

        out = StringIO()
        call_command("cleanup_deleted_employees", "--days=30", stdout=out)
        assert "Successfully permanently deleted 1 employees." in out.getvalue()
        assert Employee.objects.filter(id=emp.id).count() == 0
