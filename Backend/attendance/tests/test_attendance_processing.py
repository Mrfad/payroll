# Backend\attendance\tests\test_attendance_processing.py
import uuid
from datetime import time

import pytest
from companies.models import Company
from device.models import DeviceConfiguration, RawAttendanceLog
from django.contrib.auth.models import User
from django.utils import timezone
from employees.models import Employee

from attendance.models import (
    AttendanceRecord,
    BreakPolicy,
    OvertimePolicy,
    Shift,
    ShiftAssignment,
)
from attendance.services import AttendanceProcessingService


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
        assert processed_count == 1
        assert failed_count == 0

        log = RawAttendanceLog.objects.first()
        assert log.status == "processed"

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

    def test_process_anomalies(self, base_data):
        today = timezone.now().date()
        ShiftAssignment.objects.create(
            employee=base_data["employee"], shift=base_data["shift"], start_date=today
        )

        # Shift is 9:00 to 17:00
        # Early punch in: 8:15 (-45 mins)
        t1 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 8, 15, 0)
        )
        # Late punch out: 19:30 (+150 mins)
        t2 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 19, 30, 0)
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
        assert record.is_anomaly is True
        assert (
            "Punched out 150 minutes late" in record.anomaly_reason
            or "Punched in 45 minutes early" in record.anomaly_reason
        )

        # Late punch in: 9:45 (+45 mins)
        # Early punch out: 16:15 (-45 mins)
        today2 = today + timezone.timedelta(days=1)
        ShiftAssignment.objects.create(
            employee=base_data["employee"], shift=base_data["shift"], start_date=today2
        )
        t3 = timezone.make_aware(
            timezone.datetime(today2.year, today2.month, today2.day, 9, 45, 0)
        )
        t4 = timezone.make_aware(
            timezone.datetime(today2.year, today2.month, today2.day, 16, 15, 0)
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t3, raw_data={}
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t4, raw_data={}
        )

        AttendanceProcessingService.process_pending_logs()
        record2 = AttendanceRecord.objects.get(
            employee=base_data["employee"], date=today2
        )
        assert record2.is_anomaly is True
        assert (
            "Punched out 45 minutes early" in record2.anomaly_reason
            or "Punched in 45 minutes late" in record2.anomaly_reason
        )

    def test_process_statuses(self, base_data):
        today = timezone.now().date()
        ShiftAssignment.objects.create(
            employee=base_data["employee"], shift=base_data["shift"], start_date=today
        )

        # 1. Missing punch
        t1 = timezone.make_aware(
            timezone.datetime(today.year, today.month, today.day, 9, 0, 0)
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t1, raw_data={}
        )
        AttendanceProcessingService.process_pending_logs()
        record1 = AttendanceRecord.objects.get(
            employee=base_data["employee"], date=today
        )
        assert record1.status == "missing_punch"

        # 2. Half day (4 hours of 8 hour shift = 50%)
        today2 = today + timezone.timedelta(days=1)
        ShiftAssignment.objects.create(
            employee=base_data["employee"], shift=base_data["shift"], start_date=today2
        )
        t2 = timezone.make_aware(
            timezone.datetime(today2.year, today2.month, today2.day, 9, 0, 0)
        )
        t3 = timezone.make_aware(
            timezone.datetime(today2.year, today2.month, today2.day, 13, 0, 0)
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t2, raw_data={}
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t3, raw_data={}
        )
        AttendanceProcessingService.process_pending_logs()
        record2 = AttendanceRecord.objects.get(
            employee=base_data["employee"], date=today2
        )
        assert record2.status == "half_day"

        # 3. Absent (< 40% = < 3.2 hours)
        today3 = today + timezone.timedelta(days=2)
        ShiftAssignment.objects.create(
            employee=base_data["employee"], shift=base_data["shift"], start_date=today3
        )
        t4 = timezone.make_aware(
            timezone.datetime(today3.year, today3.month, today3.day, 9, 0, 0)
        )
        t5 = timezone.make_aware(
            timezone.datetime(today3.year, today3.month, today3.day, 11, 0, 0)
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t4, raw_data={}
        )
        RawAttendanceLog.objects.create(
            device=base_data["device"], external_id="EMP123", punch_time=t5, raw_data={}
        )
        AttendanceProcessingService.process_pending_logs()
        record3 = AttendanceRecord.objects.get(
            employee=base_data["employee"], date=today3
        )
        assert record3.status == "absent"
