# Backend\accounts\tests\test_permissions.py
import pytest
from companies.models import Company
from django.contrib.auth.models import Group, User
from employees.models import Employee
from payroll.permissions import IsManagerOrDeveloper, IsOwnerOrAdmin
from rest_framework.test import APIRequestFactory


@pytest.mark.django_db
class TestPermissions:
    def test_is_manager_or_developer(self):
        user = User.objects.create_user("manager_user", "m@test.com", "pw")
        group, _ = Group.objects.get_or_create(name="Managers")
        user.groups.add(group)

        request = APIRequestFactory().get("/")
        request.user = user
        assert IsManagerOrDeveloper().has_permission(request, None) is True

    def test_is_owner_or_admin(self):
        # Admin check
        admin = User.objects.create_superuser("admin", "admin@test.com", "pw")
        request = APIRequestFactory().get("/")
        request.user = admin

        # We need an object for has_object_permission
        company = Company.objects.create(name="Test Company")
        emp_user = User.objects.create_user("emp", "e@test.com", "pw")
        employee = Employee.objects.create(user=emp_user, company=company)

        assert IsOwnerOrAdmin().has_object_permission(request, None, employee) is True

        # Owner check
        request.user = emp_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, employee) is True

        # Not owner check
        other_user = User.objects.create_user("other", "o@test.com", "pw")
        request.user = other_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, employee) is False

    def test_unauthenticated_blocked(self, api_client):
        response = api_client.get("/api/v1/companies/companies/")
        assert response.status_code == 401

    def test_is_owner_or_admin_other_models(self):
        admin = User.objects.create_superuser("admin2", "admin2@test.com", "pw")
        company = Company.objects.create(name="Test Company 2")
        emp_user = User.objects.create_user("emp2", "e2@test.com", "pw")
        employee = Employee.objects.create(user=emp_user, company=company)

        other_user = User.objects.create_user("other2", "o2@test.com", "pw")

        from attendance.models import (
            AttendanceRecord,
            LeaveBalance,
            LeaveRequest,
            LeaveType,
        )
        from django.utils.timezone import now

        att = AttendanceRecord.objects.create(
            employee=employee, date=now().date(), first_in=now()
        )
        request = APIRequestFactory().get("/")
        request.user = emp_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, att) is True
        request.user = other_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, att) is False

        lt = LeaveType.objects.create(name="L", company=company)
        lb = LeaveBalance.objects.create(
            employee=employee, leave_type=lt, current_balance=10
        )
        request.user = emp_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, lb) is True
        request.user = other_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, lb) is False

        lr = LeaveRequest.objects.create(
            employee=employee,
            leave_type=lt,
            start_date="2025-01-01",
            end_date="2025-01-02",
            status="PENDING",
        )
        request.user = emp_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, lr) is True
        request.user = other_user
        assert IsOwnerOrAdmin().has_object_permission(request, None, lr) is False
