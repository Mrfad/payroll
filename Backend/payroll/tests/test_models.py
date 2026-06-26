import pytest
from django.contrib.auth.models import User
from payroll.models import Company, Department, Employee

@pytest.mark.django_db
class TestEmployeeModel:
    def test_employee_creation_generates_employee_id(self):
        # Arrange
        user = User.objects.create_user(username='jdoe', password='password123')
        company = Company.objects.create(name='Acme Corp')
        department = Department.objects.create(name='Engineering', company=company)
        
        # Act
        employee = Employee.objects.create(
            user=user,
            company=company,
            department=department
        )
        
        # Assert
        assert employee.employee_id is not None
        assert employee.employee_id.startswith('EMP-')
        assert len(employee.employee_id) == 12  # EMP- + 8 random chars

    def test_employee_string_representation(self):
        # Arrange
        user = User.objects.create_user(username='jdoe', password='password123')
        company = Company.objects.create(name='Acme Corp')
        
        # Act
        employee = Employee.objects.create(
            user=user,
            company=company
        )
        
        # Assert
        expected_str = f"{user.username} ({employee.employee_id})"
        assert str(employee) == expected_str

    def test_employee_save_device_user_ids_none(self):
        user = User.objects.create_user(username='no_device_user', password='pw')
        company = Company.objects.create(name='Acme Corp 2')
        employee = Employee(user=user, company=company, device_user_ids=None)
        employee.save()
        assert employee.device_user_ids == {}

@pytest.mark.django_db
class TestModelStringRepresentations:
    def test_str_methods(self):
        from payroll.models import (
            Company, Department, Shift, BreakPolicy, OvertimePolicy,
            AttendanceRecord, LeaveType, LeaveBalance, LeaveRequest,
            SalaryComponent, EmployeeSalaryStructure, PayrollPeriod,
            PayrollRun, PayrollEntry, AuditLog
        )
        from django.utils import timezone
        
        company = Company.objects.create(name="Str Company")
        assert str(company) == "Str Company"
        
        dept = Department.objects.create(company=company, name="IT")
        assert str(dept) == "IT"
        
        shift = Shift.objects.create(company=company, name="Morning", start_time="09:00:00", end_time="17:00:00")
        assert str(shift) == "Morning - Str Company"
        
        bp = BreakPolicy.objects.create(company=company, name="Lunch", duration_minutes=60)
        assert str(bp) == "Lunch"
        
        op = OvertimePolicy.objects.create(company=company, name="Standard OT", daily_threshold_hours=8.0)
        assert str(op) == "Standard OT"
        
        user = User.objects.create_user(username='str_user', password='pw')
        employee = Employee.objects.create(user=user, company=company)
        
        record = AttendanceRecord.objects.create(employee=employee, date=timezone.now().date())
        assert str(record) == f"{employee} - {record.date}"
        
        lt = LeaveType.objects.create(company=company, name="Annual")
        assert str(lt) == "Annual"
        
        lb = LeaveBalance.objects.create(employee=employee, leave_type=lt, current_balance=10)
        assert str(lb) == f"{employee} - Annual: 10"
        
        lr = LeaveRequest.objects.create(employee=employee, leave_type=lt, start_date=timezone.now().date(), end_date=timezone.now().date())
        assert str(lr) == f"{employee} - {lr.start_date} to {lr.end_date}"
        
        sc = SalaryComponent.objects.create(company=company, name="Basic", component_type='earning')
        assert str(sc) == "Basic (Str Company)"
        
        ess = EmployeeSalaryStructure.objects.create(employee=employee, component=sc, amount=1000, effective_date=timezone.now().date())
        assert str(ess) == f"{employee} - {sc}"
        
        pp = PayrollPeriod.objects.create(company=company, start_date=timezone.now().date(), end_date=timezone.now().date())
        assert str(pp) == f"Str Company - {pp.start_date} to {pp.end_date}"
        
        pr = PayrollRun.objects.create(period=pp)
        assert str(pr) == f"{pp} - Run {pr.run_date.date()}"
        
        pe = PayrollEntry.objects.create(run=pr, employee=employee)
        assert str(pe) == f"{employee} - {pp}"
        
        al = AuditLog.objects.create(action="CREATE")
        assert str(al) == "CREATE on None by None"
