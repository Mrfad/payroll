import pytest
from payroll.serializers import EmployeeEnrollmentSerializer
from payroll.models import Company

@pytest.mark.django_db
class TestSerializers:
    def test_employee_enrollment_serializer_validation(self):
        company = Company.objects.create(name='Comp')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'pw',
            'company': company.id,
            'first_name': 'First',
            'last_name': 'Last'
        }
        serializer = EmployeeEnrollmentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
    def test_employee_enrollment_serializer_missing_fields(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com'
        }
        serializer = EmployeeEnrollmentSerializer(data=data)
        assert serializer.is_valid() is False
        assert 'password' in serializer.errors
        assert 'company' in serializer.errors
