import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from payroll.models import (
    Company, Employee, PayrollPeriod, PayrollRun, PayrollEntry,
    AttendanceRecord, SalaryComponent, EmployeeSalaryStructure
)
from payroll.services.payroll import PayrollCalculationService

@pytest.fixture
def company():
    return Company.objects.create(name="TechNova Solutions")

@pytest.fixture
def employee(company):
    user = User.objects.create(username="testemp", first_name="Test", last_name="Employee")
    # Set base salary to 3000 -> daily_rate = 100, hourly_rate = 12.5
    return Employee.objects.create(
        user=user, 
        company=company, 
        employee_id="EMP-TEST", 
        base_salary=Decimal('3000.00')
    )

@pytest.fixture
def payroll_period(company):
    return PayrollPeriod.objects.create(
        company=company,
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 30),
        status='open'
    )

@pytest.mark.django_db
def test_calculate_payroll_no_attendance(company, employee, payroll_period):
    # If there is no attendance, technically they are all 'absent' if they should have been working.
    # Wait, our current engine just iterates over existing AttendanceRecords to find absences/overtime.
    # If no records exist, the engine does NOT deduct anything for absences currently (it assumes full pay).
    # Let's test that it calculates base salary correctly.
    
    run = PayrollCalculationService.calculate_payroll(payroll_period.id)
    
    entry = PayrollEntry.objects.get(run=run, employee=employee)
    assert entry.gross_earnings == Decimal('3000.00')
    assert entry.total_deductions == Decimal('0.00')
    assert entry.net_pay == Decimal('3000.00')

@pytest.mark.django_db
def test_calculate_payroll_with_absences_and_overtime(company, employee, payroll_period):
    # Add an allowance
    allowance = SalaryComponent.objects.create(
        company=company, name="Housing", component_type="earning"
    )
    EmployeeSalaryStructure.objects.create(
        employee=employee, component=allowance, amount=Decimal('500.00'), effective_date=date(2026, 1, 1)
    )
    
    # 2 absent days
    AttendanceRecord.objects.create(
        employee=employee, date=date(2026, 6, 5), status="absent"
    )
    AttendanceRecord.objects.create(
        employee=employee, date=date(2026, 6, 6), status="absent"
    )
    
    # 1 half day
    AttendanceRecord.objects.create(
        employee=employee, date=date(2026, 6, 7), status="half_day"
    )
    
    # 4 hours overtime on another day (14400 seconds)
    AttendanceRecord.objects.create(
        employee=employee, date=date(2026, 6, 8), status="present", overtime_seconds=14400
    )
    
    # Expected calculations:
    # Base Salary: 3000
    # Allowance: 500
    # Total Gross Base: 3500
    
    # daily_rate = 3000 / 30 = 100
    # hourly_rate = 100 / 8 = 12.5
    
    # Deductions:
    # 2 absent days = 2 * 100 = 200
    # 1 half day = 0.5 * 100 = 50
    # Total Deductions: 250
    
    # Overtime:
    # 4 hours * 12.5 * 1.5 = 75
    
    # Gross Earnings: 3000 (base) + 500 (allowance) + 75 (overtime) = 3575
    # Net Pay = 3575 - 250 = 3325
    
    run = PayrollCalculationService.calculate_payroll(payroll_period.id)
    entry = PayrollEntry.objects.get(run=run, employee=employee)
    
    assert entry.gross_earnings == Decimal('3575.00')
    assert entry.total_deductions == Decimal('250.00')
    assert entry.net_pay == Decimal('3325.00')
    
    # Check JSON breakdown
    assert len(entry.details['earnings']) == 3  # Base, Housing, Overtime
    assert len(entry.details['deductions']) == 2 # Absent, Half Day
    assert entry.details['attendance_summary']['total_overtime_hours'] == 4.0

@pytest.mark.django_db
def test_calculate_payroll_with_deduction_component(company, employee, payroll_period):
    deduction = SalaryComponent.objects.create(
        company=company, name="Health Insurance", component_type="deduction"
    )
    EmployeeSalaryStructure.objects.create(
        employee=employee, component=deduction, amount=Decimal('200.00'), effective_date=date(2026, 1, 1)
    )
    
    run = PayrollCalculationService.calculate_payroll(payroll_period.id)
    entry = PayrollEntry.objects.get(run=run, employee=employee)
    
    # Base Salary: 3000
    # Deduction: 200
    # Net Pay = 2800
    assert entry.gross_earnings == Decimal('3000.00')
    assert entry.total_deductions == Decimal('200.00')
    assert entry.net_pay == Decimal('2800.00')

@pytest.mark.django_db
def test_calculate_payroll_fallback_overtime_rate(company, employee, payroll_period):
    # Overtime without a shift assignment should use 1.5 multiplier as fallback
    # employee base salary 3000 -> 100/day -> 12.5/hour
    # overtime 4 hours -> 4 * 12.5 * 1.5 = 75
    AttendanceRecord.objects.create(
        employee=employee, date=date(2026, 6, 8), status="present", overtime_seconds=14400
    )
    
    run = PayrollCalculationService.calculate_payroll(payroll_period.id)
    entry = PayrollEntry.objects.get(run=run, employee=employee)
    
    assert entry.gross_earnings == Decimal('3075.00')
    assert entry.net_pay == Decimal('3075.00')
    
    # Verify the detail block contains overtime 
    overtime_detail = next((item for item in entry.details['earnings'] if item['name'].startswith('Overtime')), None)
    assert overtime_detail is not None
    assert overtime_detail['amount'] == 75.0
