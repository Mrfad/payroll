import uuid
from datetime import time

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from device.models import DeviceConfiguration, RawAttendanceLog
from payroll.models import (
    AttendanceRecord,
    BreakPolicy,
    Company,
    Employee,
    OvertimePolicy,
    Shift,
    ShiftAssignment,
)
from payroll.services.attendance import AttendanceProcessingService


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
    shift = Shift.objects.create(
        company=company, name="Day Shift", start_time=time(9, 0), end_time=time(17, 0)
    )  # 8 hours

    return {"company": company, "employee": employee, "device": device, "shift": shift}


@pytest.mark.django_db
class TestAttendanceProcessingService:
    def test_process_basic_punch_pair(self, base_data, mocker):
        # Mocker to avoid user creation signal issues if any, but let's assume it works
        # Create a shift assignment
        today = timezone.now().date()
        ShiftAssignment.objects.create(
            employee=base_data["employee"], shift=base_data["shift"], start_date=today
        )

        # Create raw logs
        t1 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 9, 0, 0)
        )
        t2 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 17, 0, 0)
        )

        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t1, raw_data={}
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t2, raw_data={}
        )

        processed_count, failed_count = (
            AttendanceProcessingService.process_pending_logs()
        )
        assert processed_count == 2
        assert failed_count == 0

        # Verify AttendanceRecord
        record = AttendanceRecord.objects.get(
            employee=base_data["employee"], date=today
        )
        assert record.status == "present"
        assert record.total_work_seconds == 8 * 3600
        assert record.overtime_seconds == 0
        assert record.first_in == t1
        assert record.last_out == t2
        assert record.raw_logs.count() == 2

        # Verify logs are processed
        assert RawAttendanceLog.objects.filter(status="processed").count() == 2

    def test_process_unmapped_employee(self, base_data):
        today = timezone.now().date()
        t1 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 9, 0, 0)
        )

        RawAttendanceLog.objects.create(
            device=base_data["device"],
            external_id="UNKNOWN_999",
            punch_time=t1,
            raw_data={},
        )

        processed_count, failed_count = (
            AttendanceProcessingService.process_pending_logs()
        )
        assert processed_count == 0
        assert failed_count == 1

        log = RawAttendanceLog.objects.first()
        assert log.status == "failed"

    def test_process_overtime(self, base_data):
        today = timezone.now().date()
        ot_policy = OvertimePolicy.objects.create(
            company=base_data["company"], name="Standard OT", daily_threshold_hours=8.0
        )
        ShiftAssignment.objects.create(
            employee=base_data["employee"],
            shift=base_data["shift"],
            start_date=today,
            overtime_policy=ot_policy,
        )

        # 10 hours of work
        t1 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 8, 0, 0)
        )
        t2 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 18, 0, 0)
        )

        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t1, raw_data={}
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t2, raw_data={}
        )

        AttendanceProcessingService.process_pending_logs()

        record = AttendanceRecord.objects.get(
            employee=base_data["employee"], date=today
        )
        assert record.total_work_seconds == 10 * 3600
        assert record.overtime_seconds == 2 * 3600

    def test_process_break_deduction(self, base_data):
        today = timezone.now().date()
        bp = BreakPolicy.objects.create(
            company=base_data["company"],
            name="Lunch",
            duration_minutes=60,
            is_paid=False,
        )
        sa = ShiftAssignment.objects.create(
            employee=base_data["employee"], shift=base_data["shift"], start_date=today
        )
        sa.break_policies.add(bp)

        # 9 hours total, 1 hour unpaid break => 8 hours work
        t1 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 9, 0, 0)
        )
        t2 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 18, 0, 0)
        )

        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t1, raw_data={}
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t2, raw_data={}
        )

        AttendanceProcessingService.process_pending_logs()

        record = AttendanceRecord.objects.get(
            employee=base_data["employee"], date=today
        )
        assert record.total_work_seconds == 8 * 3600
