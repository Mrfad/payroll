# Backend\attendance\models.py
from common.models import TimeStampedModel
from companies.models import Company
from django.db import models
from employees.models import Employee


class Shift(TimeStampedModel):
    """
    Defines a standard working schedule (e.g., 9 AM to 5 PM).
    Used to evaluate employee attendance, lateness, and overtime.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = "payroll_shift"
        unique_together = [("company", "name")]

    def __str__(self):
        return f"{self.name} - {self.company.name}"


class BreakPolicy(TimeStampedModel):
    """
    Defines rules for employee breaks during a Shift (e.g., 1 hour lunch break).
    Used to calculate net working hours and deduct unpaid break times.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    class Meta:
        db_table = "payroll_breakpolicy"

    def __str__(self):
        return self.name


class OvertimePolicy(TimeStampedModel):
    """
    Defines rules and rates for calculating overtime pay.
    Determines how hours worked beyond the standard shift are compensated.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    daily_threshold_hours = models.DecimalField(max_digits=4, decimal_places=2)
    weekly_threshold_hours = models.DecimalField(
        max_digits=4, decimal_places=2, null=True
    )
    rate_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)

    class Meta:
        db_table = "payroll_overtimepolicy"

    def __str__(self):
        return self.name


class ShiftAssignment(TimeStampedModel):
    """
    Maps an Employee to a specific Shift.
    Allows for flexible scheduling where employees might have different shifts on different days.
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    break_policies = models.ManyToManyField(BreakPolicy, blank=True)
    overtime_policy = models.ForeignKey(
        OvertimePolicy, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        db_table = "payroll_shiftassignment"

    def __str__(self):
        return f"{self.employee} - {self.shift}"


class AttendanceRecord(TimeStampedModel):
    """
    Records an employee's daily attendance, including clock-in and clock-out times.
    Used by the payroll calculation engine to determine hours worked and absences.
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift_assignment = models.ForeignKey(
        ShiftAssignment, null=True, blank=True, on_delete=models.SET_NULL
    )
    date = models.DateField()
    first_in = models.DateTimeField(null=True, blank=True)
    last_out = models.DateTimeField(null=True, blank=True)
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    total_work_seconds = models.PositiveIntegerField(default=0)
    overtime_seconds = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ("present", "Present"),
            ("absent", "Absent"),
            ("half_day", "Half Day"),
            ("holiday", "Holiday"),
            ("weekend", "Weekend"),
            ("missing_punch", "Missing Punch"),
        ],
    )
    is_anomaly = models.BooleanField(default=False)
    anomaly_reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "payroll_attendancerecord"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"], name="unique_attendance_per_day"
            )
        ]

    def __str__(self):
        return f"{self.employee} - {self.date}"


class LeaveType(TimeStampedModel):
    """
    Defines categories of time off (e.g., Annual Leave, Sick Leave).
    Determines whether the leave is paid or unpaid and the default accrual rules.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_paid = models.BooleanField(default=True)
    accrual_rule = models.JSONField(default=dict, blank=True)
    max_balance = models.DecimalField(max_digits=5, decimal_places=1, null=True)

    class Meta:
        db_table = "payroll_leavetype"

    def __str__(self):
        return self.name


class LeaveBalance(TimeStampedModel):
    """
    Tracks the amount of leave an employee has accrued and taken for a specific LeaveType.
    Ensures employees do not exceed their allowed time off.
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    current_balance = models.DecimalField(max_digits=5, decimal_places=1)

    class Meta:
        db_table = "payroll_leavebalance"

    def __str__(self):
        return f"{self.employee} - {self.leave_type}: {self.current_balance}"


class LeaveRequest(TimeStampedModel):
    """
    Represents an employee's application for time off.
    Tracks the approval workflow (pending, approved, rejected) and dates requested.
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
    )
    approved_by = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_leaves",
    )
    deduction_days = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    class Meta:
        db_table = "payroll_leaverequest"

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date}"
