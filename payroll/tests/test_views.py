import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from payroll.models import Company, Department, Employee

@pytest.mark.django_db
class TestEmployeeViewSet:
    
    def test_get_active_employees(self, auth_client, employee):
        # Arrange
        # Soft delete a second employee to verify filtering
        user2 = User.objects.create_user(username='employee_2', password='pw')
        deleted_employee = Employee.objects.create(
            user=user2, company=employee.company, 
            deleted_at=timezone.now(), is_active=False
        )
        
        # Act
        response = auth_client.get('/api/v1/payroll/employees/')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # The DRF response is paginated, so data is in 'results'
        results = response.data['results'] if 'results' in response.data else response.data
        
        assert len(results) == 1
        assert results[0]['id'] == employee.id
        
    def test_retrieve_employee(self, auth_client, employee):
        response = auth_client.get(f'/api/v1/payroll/employees/{employee.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == employee.id

    def test_create_employee(self, auth_client, company, department):
        new_user = User.objects.create_user(username='new_emp_user', password='pw')
        payload = {
            'user': new_user.id,
            'company': company.id,
            'department': department.id,
        }
        response = auth_client.post('/api/v1/payroll/employees/', data=payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user'] == new_user.id
        
    def test_get_deleted_employees(self, auth_client, employee):
        # Arrange
        user2 = User.objects.create_user(username='employee_2', password='pw')
        deleted_employee = Employee.objects.create(
            user=user2, company=employee.company, 
            deleted_at=timezone.now(), is_active=False
        )
        
        # Act
        response = auth_client.get('/api/v1/payroll/employees/?show_deleted=true')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        results = response.data['results'] if 'results' in response.data else response.data
        
        assert len(results) == 1
        assert results[0]['id'] == deleted_employee.id

    def test_soft_delete_employee(self, auth_client, employee):
        # Act
        response = auth_client.delete(f'/api/v1/payroll/employees/{employee.id}/')
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify in database
        employee.refresh_from_db()
        assert employee.deleted_at is not None
        assert employee.is_active is False
        assert employee.user.is_active is False

    def test_restore_employee(self, auth_client, employee):
        # Arrange
        employee.deleted_at = timezone.now()
        employee.is_active = False
        employee.save()
        
        # Act
        response = auth_client.post(f'/api/v1/payroll/employees/{employee.id}/restore/?show_deleted=true')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        employee.refresh_from_db()
        assert employee.deleted_at is None
        assert employee.is_active is True

    def test_enroll_employee(self, auth_client, company, department):
        # Act
        payload = {
            'username': 'new_user_1',
            'password': 'pw',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@test.com',
            'company': company.id,
            'department': department.id,
        }
        response = auth_client.post('/api/v1/payroll/employees/enroll/', data=payload, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert 'employee_id' in response.data

    def test_perform_update_freeze(self, auth_client, employee):
        # Act
        response = auth_client.patch(f'/api/v1/payroll/employees/{employee.id}/', data={'is_active': False}, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        employee.refresh_from_db()
        assert employee.is_active is False

@pytest.mark.django_db
class TestDashboardViewSet:
    def test_dashboard_data(self, auth_client, employee):
        response = auth_client.get('/api/v1/payroll/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_employees' in response.data
        assert response.data['total_employees'] == 1

    def test_dashboard_empty_db(self, auth_client):
        # Delete the fixture employee to test empty DB
        Employee.objects.all().delete()
        response = auth_client.get('/api/v1/payroll/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_employees' in response.data
        assert response.data['total_employees'] == 0
