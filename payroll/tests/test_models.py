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
