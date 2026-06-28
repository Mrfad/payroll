# Backend\payroll\models.py
import uuid

from common.models import TimeStampedModel
from companies.models import Company, Department
from django.conf import settings
from django.db import models
from employees.models import Employee


class SalaryComponent(TimeStampedModel):
    """
    Defines individual parts of a salary (e.g., Basic Pay, Housing Allowance, Tax Deduction).
    Components can be earnings or deductions and are used to construct a salary structure.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Basic, Housing Allowance, Overtime
    component_type = models.CharField(
        max_length=20, choices=[("earning", "Earning"), ("deduction", "Deduction")]
    )
    calculation_method = models.CharField(
        max_length=50,
        default="fixed",  # 'fixed', 'formula', 'python_code'
        help_text="fixed, percentage, or a callable string",
    )
    formula = models.TextField(
        blank=True
    )  # e.g., "basic * 0.4" or a Python code snippet for complex rules

    def __str__(self):
        return f"{self.name} ({self.company})"


class EmployeeSalaryStructure(TimeStampedModel):
    """
    Maps a SalaryComponent to a specific Employee with an assigned monetary amount.
    Represents the employee's individualized compensation package.
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )  # fixed amount
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # for formula-based
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.component}"


class PayrollPeriod(TimeStampedModel):
    """
    Defines a specific time frame (e.g., January 2026) for which payroll is calculated.
    Groups all payroll runs and attendance records for a specific cycle.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default="open")

    def __str__(self):
        return f"{self.company} - {self.start_date} to {self.end_date}"


class PayrollRun(TimeStampedModel):
    """
    Represents the execution of a payroll calculation for a specific Employee in a PayrollPeriod.
    Stores the finalized gross pay, total deductions, and net pay.
    """

    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)
    run_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="draft")

    def __str__(self):
        return f"{self.period} - Run {self.run_date.date()}"


class PayrollEntry(TimeStampedModel):
    """
    Stores the detailed breakdown of a PayrollRun (line items).
    Records the exact amount for each SalaryComponent during that specific payroll cycle.
    """

    run = models.ForeignKey(
        PayrollRun, on_delete=models.CASCADE, related_name="entries"
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    gross_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    details = models.JSONField(default=dict, blank=True)  # breakdown per component

    def __str__(self):
        return f"{self.employee} - {self.run.period}"
