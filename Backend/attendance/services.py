# Backend\attendance\services.py
import datetime
import logging
from collections import defaultdict

from companies.models import Company, Department
from device.models import RawAttendanceLog
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from employees.models import Employee

from attendance.models import AttendanceRecord, ShiftAssignment

logger = logging.getLogger(__name__)


class AttendanceProcessingService:
    @classmethod
    def get_employee_by_external_id(cls, external_id, device_type):
        """
        Attempts to resolve an employee based on their core employee_id,
        or a device-specific mapping in device_user_ids.
        """
        query = Q(employee_id=external_id)
        if device_type:
            query |= Q(**{f"device_user_ids__{device_type}": external_id})
        return Employee.objects.filter(query).first()

    @classmethod
    def process_pending_logs(cls):
        """
        Processes all pending RawAttendanceLogs.
        Groups them by employee and calendar date, then calculates total work time,
        overtime, and attendance status.
        """
        # Process both pending and previously-failed logs.
        # Failed logs are retried in case the employee was created since.
        logs_to_process = RawAttendanceLog.objects.filter(
            status__in=["pending", "failed"]
        ).order_by("punch_time")

        if not logs_to_process.exists():
            return 0, 0

        # Group logs by external_id, device_type, and local calendar date
        grouped_logs = defaultdict(list)
        for log in logs_to_process:
            # Note: For Night Shifts crossing midnight, this simple local_date grouping
            # assigns the punch to the calendar day it occurred.
            local_date = timezone.localtime(log.punch_time).date()
            device_type = log.device.device_type if log.device else None
            grouped_logs[(log.external_id, device_type, local_date)].append(log)

        processed_count = 0
        failed_count = 0

        with transaction.atomic():
            for (external_id, device_type, date), logs in grouped_logs.items():
                employee = cls.get_employee_by_external_id(external_id, device_type)

                if not employee:
                    # Auto-enroll unknown employee from device
                    logger.info(
                        f"Auto-creating employee for external_id='{external_id}' (device_type='{device_type}')"
                    )
                    import uuid

                    from django.contrib.auth.models import User

                    # Fallback to first company if device company is missing
                    company = (
                        logs[0].device.company
                        if logs and logs[0].device
                        else Company.objects.first()
                    )

                    if company:
                        department, _ = Department.objects.get_or_create(
                            company=company, name="Unassigned (From Device)"
                        )

                        # Generate a safe username
                        safe_username = f"dev_user_{external_id.lower().replace(' ', '_')}_{str(uuid.uuid4())[:6]}"

                        user, _ = User.objects.get_or_create(
                            username=safe_username,
                            defaults={
                                "first_name": "Unknown",
                                "last_name": "Device User",
                            },
                        )
                        user.set_unusable_password()
                        user.save()

                        employee = Employee.objects.create(
                            employee_id=external_id,
                            company=company,
                            department=department,
                            user=user,
                            is_active=True,
                        )
                        if device_type:
                            employee.device_user_ids = {device_type: external_id}
                            employee.save()
                    else:
                        logger.warning(
                            f"Cannot auto-create employee for {external_id} because no exists. Logs kept pending."
                        )
                        failed_count += len(logs)
                        continue

                # Find or create AttendanceRecord
                record, created = AttendanceRecord.objects.get_or_create(
                    employee=employee,
                    date=date,
                    defaults={
                        "status": "absent",
                        "total_work_seconds": 0,
                        "overtime_seconds": 0,
                    },
                )

                # Collect existing punches from the record + new punches
                all_punches = [timezone.localtime(log.punch_time) for log in logs]
                if record.first_in:
                    all_punches.append(timezone.localtime(record.first_in))
                if record.last_out:
                    all_punches.append(timezone.localtime(record.last_out))

                all_punches.sort()
                record.first_in = all_punches[0]

                if len(all_punches) > 1:
                    record.last_out = all_punches[-1]
                    duration = (record.last_out - record.first_in).total_seconds()
                else:
                    record.last_out = None
                    duration = 0

                # Fetch active ShiftAssignment for this date
                shift_assignment = (
                    ShiftAssignment.objects.filter(
                        employee=employee, start_date__lte=date
                    )
                    .filter(Q(end_date__isnull=True) | Q(end_date__gte=date))
                    .order_by("-start_date")
                    .first()
                )

                record.shift_assignment = shift_assignment

                # Simple Break Deduction
                break_seconds = 0
                if shift_assignment:
                    for bp in shift_assignment.break_policies.all():
                        if bp.duration_minutes and not bp.is_paid:
                            break_seconds += bp.duration_minutes * 60

                work_seconds = max(0, int(duration - break_seconds))
                record.total_work_seconds = work_seconds

                # Simple Overtime/Status logic
                expected_hours = 8  # Default fallback
                if shift_assignment and shift_assignment.shift:
                    st = shift_assignment.shift.start_time
                    et = shift_assignment.shift.end_time

                    td_st = timezone.timedelta(hours=st.hour, minutes=st.minute)
                    td_et = timezone.timedelta(hours=et.hour, minutes=et.minute)
                    if td_et < td_st:  # Crosses midnight
                        td_et += timezone.timedelta(days=1)

                    expected_seconds = (td_et - td_st).total_seconds()
                    expected_hours = expected_seconds / 3600

                # Shift Anomaly Check
                record.is_anomaly = False
                record.anomaly_reason = None

                if shift_assignment and shift_assignment.shift:
                    st = shift_assignment.shift.start_time
                    et = shift_assignment.shift.end_time

                    fi_time = timezone.localtime(record.first_in).time()
                    dummy_date = datetime.date.today()
                    fi_dt = datetime.datetime.combine(dummy_date, fi_time)
                    st_dt = datetime.datetime.combine(dummy_date, st)

                    diff_in = (fi_dt - st_dt).total_seconds() / 60.0

                    if diff_in < -30:
                        record.is_anomaly = True
                        record.anomaly_reason = (
                            f"Punched in {abs(int(diff_in))} minutes early"
                        )
                    elif diff_in > 30:
                        record.is_anomaly = True
                        record.anomaly_reason = (
                            f"Punched in {int(diff_in)} minutes late"
                        )

                    if not record.is_anomaly and record.last_out:
                        lo_time = timezone.localtime(record.last_out).time()
                        lo_dt = datetime.datetime.combine(dummy_date, lo_time)
                        et_dt = datetime.datetime.combine(dummy_date, et)

                        if et < st:
                            et_dt += datetime.timedelta(days=1)
                            if lo_time < st:
                                lo_dt += datetime.timedelta(days=1)
                        elif lo_time < st and fi_time >= st:
                            lo_dt += datetime.timedelta(days=1)

                        diff_out = (lo_dt - et_dt).total_seconds() / 60.0
                        if diff_out < -30:
                            record.is_anomaly = True
                            record.anomaly_reason = (
                                f"Punched out {abs(int(diff_out))} minutes early"
                            )
                        elif diff_out > 120:
                            record.is_anomaly = True
                            record.anomaly_reason = (
                                f"Punched out {int(diff_out)} minutes late"
                            )

                # Status updates
                if len(all_punches) == 1:
                    record.status = "missing_punch"
                elif work_seconds > 0:
                    if work_seconds >= (expected_hours * 3600 * 0.9):  # 90% of expected
                        record.status = "present"
                    elif work_seconds >= (
                        expected_hours * 3600 * 0.4
                    ):  # 40% of expected
                        record.status = "half_day"
                    else:
                        record.status = "absent"
                else:
                    record.status = "absent"

                # Overtime calculation
                overtime_threshold = expected_hours * 3600
                if shift_assignment and shift_assignment.overtime_policy:
                    overtime_threshold = (
                        float(shift_assignment.overtime_policy.daily_threshold_hours)
                        * 3600
                    )

                if work_seconds > overtime_threshold:
                    record.overtime_seconds = int(work_seconds - overtime_threshold)
                else:
                    record.overtime_seconds = 0

                record.save()

                # Update logs
                for log in logs:
                    log.status = "processed"
                    log.processed_at = timezone.now()
                    log.save()
                    record.raw_logs.add(log)

                processed_count += len(logs)

        return processed_count, failed_count
