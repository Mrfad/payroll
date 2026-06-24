# payroll/models.py
from django.db import models
from django.conf import settings
import uuid

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

class Company(TimeStampedModel):
    name = models.CharField(max_length=255)
    # ... address, tax_id, etc.

    def __str__(self):
        return self.name

class Department(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Employee(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    employee_id = models.CharField(max_length=50, unique=True, blank=True)  # internal ID
    device_user_ids = models.JSONField(default=dict, blank=True)  # {"device_type": "external_id"}
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # ... personal info, hire_date, termination_date

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        if self.device_user_ids is None:
            self.device_user_ids = {}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.employee_id})"

class Shift(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # advanced features: flexible start/end windows, grace periods

    def __str__(self):
        return f"{self.name} - {self.company.name}"

class BreakPolicy(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    # can be linked to a shift or applied globally

    def __str__(self):
        return self.name

class OvertimePolicy(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    daily_threshold_hours = models.DecimalField(max_digits=4, decimal_places=2)  # e.g., 8
    weekly_threshold_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    rate_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)
    # complex: different rates for weekends/holidays – can be a JSON formula later

    def __str__(self):
        return self.name

class ShiftAssignment(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    break_policies = models.ManyToManyField(BreakPolicy, blank=True)
    overtime_policy = models.ForeignKey(OvertimePolicy, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.employee} - {self.shift}"

class AttendanceRecord(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift_assignment = models.ForeignKey(ShiftAssignment, null=True, on_delete=models.SET_NULL)
    date = models.DateField()
    first_in = models.DateTimeField(null=True)
    last_out = models.DateTimeField(null=True)
    break_start = models.DateTimeField(null=True)
    break_end = models.DateTimeField(null=True)
    total_work_seconds = models.PositiveIntegerField(default=0)
    overtime_seconds = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('present','Present'),('absent','Absent'),('half_day','Half Day'),('holiday','Holiday'),('weekend','Weekend')
    ])
    raw_logs = models.ManyToManyField('device.RawAttendanceLog', blank=True)
    # computed fields stored for payroll performance

    def __str__(self):
        return f"{self.employee} - {self.date}"

class LeaveType(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Annual, Sick, Unpaid, etc.
    is_paid = models.BooleanField(default=True)
    accrual_rule = models.JSONField(default=dict, blank=True)  # e.g., {"type":"monthly", "hours":1.5}
    max_balance = models.DecimalField(max_digits=5, decimal_places=1, null=True)

    def __str__(self):
        return self.name

class LeaveBalance(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    current_balance = models.DecimalField(max_digits=5, decimal_places=1)
    # transaction logs could be separate

    def __str__(self):
        return f"{self.employee} - {self.leave_type}: {self.current_balance}"

class LeaveRequest(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending',
                              choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')])
    approved_by = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_leaves')
    deduction_days = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date}"

class SalaryComponent(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Basic, Housing Allowance, Overtime
    component_type = models.CharField(max_length=20, choices=[('earning','Earning'),('deduction','Deduction')])
    calculation_method = models.CharField(max_length=50, default='fixed',  # 'fixed', 'formula', 'python_code'
                                          help_text="fixed, percentage, or a callable string")
    formula = models.TextField(blank=True)  # e.g., "basic * 0.4" or a Python code snippet for complex rules

    def __str__(self):
        return f"{self.name} ({self.company})"

class EmployeeSalaryStructure(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # fixed amount
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # for formula-based
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.component}"

class PayrollPeriod(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='open')

    def __str__(self):
        return f"{self.company} - {self.start_date} to {self.end_date}"

class PayrollRun(TimeStampedModel):
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)
    run_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='draft')

    def __str__(self):
        return f"{self.period} - Run {self.run_date.date()}"

class PayrollEntry(TimeStampedModel):
    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='entries')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    gross_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    details = models.JSONField(default=dict, blank=True)  # breakdown per component

    def __str__(self):
        return f"{self.employee} - {self.run.period}"