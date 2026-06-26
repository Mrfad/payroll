# pyrefly: ignore [missing-import]
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
# pyrefly: ignore [missing-import]
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

    def test_employee_punch(self, auth_client, employee, company):
        # We need to test the /employees/{id}/punch/ endpoint
        response = auth_client.post(f'/api/v1/payroll/employees/{employee.id}/punch/', format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'Punch recorded successfully'
        
        # Verify a device was created
        from device.models import DeviceConfiguration, RawAttendanceLog
        device = DeviceConfiguration.objects.filter(company=company, name="App Punch").first()
        assert device is not None
        
        # Verify a raw log was created
        log = RawAttendanceLog.objects.filter(device=device, external_id=employee.employee_id).first()
        assert log is not None
        
        # Verify attendance processing was triggered and record exists
        from payroll.models import AttendanceRecord
        record = AttendanceRecord.objects.filter(employee=employee, date=timezone.now().date()).first()
        assert record is not None
        assert record.raw_logs.count() == 1

    def test_perform_update_audit_diff(self, auth_client, employee):
        from payroll.models import AuditLog
        
        # Change base salary to trigger audit log diff
        response = auth_client.patch(
            f'/api/v1/payroll/employees/{employee.id}/', 
            data={'base_salary': '5000.00', 'is_active': False}, 
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify AuditLog was created for FREEZE and diff
        logs = AuditLog.objects.filter(target_user=employee.user)
        assert logs.filter(action="FREEZE").exists()
        
        update_log = logs.filter(action="UPDATE").first()
        if update_log:
            assert 'base_salary' in update_log.details
            assert '5000.00' in update_log.details

    def test_get_employees_filtering_non_staff(self, employee):
        from rest_framework.test import APIClient
        client = APIClient()
        # Authenticate as the employee (not staff)
        client.force_authenticate(user=employee.user)
        
        # Create another employee
        user2 = User.objects.create_user(username='employee_2', password='pw')
        Employee.objects.create(user=user2, company=employee.company)
        
        response = client.get('/api/v1/payroll/employees/')
        assert response.status_code == status.HTTP_200_OK
        
        results = response.data['results'] if 'results' in response.data else response.data
        # Should only see themselves
        assert len(results) == 1
        assert results[0]['id'] == employee.id

    def test_employee_unfreeze_audit(self, auth_client, employee):
        # Freeze first
        employee.is_active = False
        employee.save()
        
        # Now unfreeze
        response = auth_client.patch(
            f'/api/v1/payroll/employees/{employee.id}/', 
            data={'is_active': True}, 
            format='json'
        )
        assert response.status_code == 200
        
        # Verify UNFREEZE audit log
        from payroll.models import AuditLog
        logs = AuditLog.objects.filter(target_user=employee.user)
        assert logs.filter(action="UNFREEZE").exists()

    def test_employee_punch(self, auth_client, employee, mocker):
        from device.models import DeviceConfiguration, RawAttendanceLog
        device = DeviceConfiguration.objects.create(
            name="Test Device", device_type="zkteco", company=employee.company, ip_address="192.168.1.100"
        )
        
        mock_process = mocker.patch('payroll.services.attendance.AttendanceProcessingService.process_pending_logs')
        
        response = auth_client.post(
            f'/api/v1/payroll/employees/{employee.id}/punch/',
            data={'device_id': device.id},
            format='json'
        )
        assert response.status_code == 201
        assert "Punch recorded" in response.data['status']
        
        # Verify raw log created
        log = RawAttendanceLog.objects.filter(device__name="App Punch", external_id=employee.employee_id).first()
        assert log is not None
        assert log.status == "pending"
        
        # Verify processing was triggered
        mock_process.assert_called_once()

    def test_enroll_permission(self, auth_client, employee):
        response = auth_client.post('/api/v1/payroll/employees/enroll/', data={
            'username': 'new_enroll_user',
            'email': 'enroll@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'Enroll',
            'last_name': 'Test',
            'company': employee.company.id,
            'department': employee.department.id,
            'base_salary': '60000.00'
        }, format='json')
        assert response.status_code == 201

    def test_enroll_permission_unauthenticated(self, client, employee):
        response = client.post('/api/v1/payroll/employees/enroll/', data={
            'username': 'new_enroll_user',
            'email': 'enroll@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'Enroll',
            'last_name': 'Test',
            'company': employee.company.id,
            'department': employee.department.id,
            'base_salary': '60000.00'
        }, format='json')
        assert response.status_code == 401

@pytest.mark.django_db
class TestPayrollEntryViewSet:
    def test_payroll_entry_filtering_non_staff(self, employee):
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=employee.user)
        
        from payroll.models import PayrollRun, PayrollPeriod, PayrollEntry
        period = PayrollPeriod.objects.create(company=employee.company, start_date=timezone.now().date(), end_date=timezone.now().date(), status='open')
        run = PayrollRun.objects.create(period=period)
        
        PayrollEntry.objects.create(run=run, employee=employee, net_pay=100)
        
        # Another employee's entry
        user2 = User.objects.create_user(username='employee_2', password='pw')
        emp2 = Employee.objects.create(user=user2, company=employee.company)
        PayrollEntry.objects.create(run=run, employee=emp2, net_pay=200)
        
        response = client.get('/api/v1/payroll/payroll-entries/')
        assert response.status_code == status.HTTP_200_OK
        
        results = response.data['results'] if 'results' in response.data else response.data
        assert len(results) == 1
        assert results[0]['employee'] == employee.id

@pytest.mark.django_db
class TestUserProfileViewSet:
    def test_user_profile_theme_broadcast(self, employee, mocker):
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=employee.user)
        
        # Mock the channel layer
        mock_channel_layer = mocker.patch('channels.layers.get_channel_layer')
        mock_async_to_sync = mocker.patch('asgiref.sync.async_to_sync')
        
        response = client.patch('/api/v1/payroll/user-profile/me/', data={'theme': 'dark'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Verify broadcast
        mock_async_to_sync.assert_called_once()

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
