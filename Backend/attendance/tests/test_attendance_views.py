# Backend\attendance\tests\test_attendance_views.py
import pytest
from django.utils.timezone import now
from rest_framework import status

from attendance.models import AttendanceRecord, LeaveBalance, LeaveRequest, LeaveType


@pytest.fixture
def attendance(employee):
    return AttendanceRecord.objects.create(
        employee=employee, date=now().date(), first_in=now()
    )


@pytest.fixture
def leave_type(company):
    return LeaveType.objects.create(name="Annual", company=company)


@pytest.fixture
def leave_balance(employee, leave_type):
    return LeaveBalance.objects.create(
        employee=employee, leave_type=leave_type, current_balance=20
    )


@pytest.mark.django_db
class TestAttendanceRecordViewSet:
    def test_list_attendance(self, auth_client, attendance):
        response = auth_client.get("/api/v1/attendance/attendance-records/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_attendance(self, auth_client, employee):
        response = auth_client.post(
            "/api/v1/attendance/attendance-records/",
            {
                "employee": employee.id,
                "date": "2025-10-10",
                "first_in": "2025-10-10T09:00:00Z",
                "status": "present",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data

    def test_delete_attendance(self, auth_client, attendance):
        response = auth_client.delete(
            f"/api/v1/attendance/attendance-records/{attendance.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestLeaveTypeViewSet:
    def test_list_leave_types(self, auth_client, leave_type):
        response = auth_client.get("/api/v1/attendance/leave-types/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_leave_type(self, auth_client, company):
        response = auth_client.post(
            "/api/v1/attendance/leave-types/",
            {"name": "Sick", "company": company.id, "is_paid": True},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_leave_type(self, auth_client, leave_type):
        response = auth_client.delete(
            f"/api/v1/attendance/leave-types/{leave_type.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestLeaveBalanceViewSet:
    def test_list_leave_balances(self, auth_client, leave_balance):
        response = auth_client.get("/api/v1/attendance/leave-balances/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_leave_balance(self, auth_client, employee, leave_type):
        response = auth_client.post(
            "/api/v1/attendance/leave-balances/",
            {
                "employee": employee.id,
                "leave_type": leave_type.id,
                "current_balance": 10,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_leave_balance(self, auth_client, leave_balance):
        response = auth_client.delete(
            f"/api/v1/attendance/leave-balances/{leave_balance.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestLeaveRequestViewSet:
    def test_list_leave_requests(self, auth_client, employee, leave_type):
        LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date="2025-01-01",
            end_date="2025-01-05",
            status="PENDING",
        )
        response = auth_client.get("/api/v1/attendance/leave-requests/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_leave_request(self, auth_client, employee, leave_type):
        response = auth_client.post(
            "/api/v1/attendance/leave-requests/",
            {
                "employee": employee.id,
                "leave_type": leave_type.id,
                "start_date": "2025-11-01",
                "end_date": "2025-11-02",
                "reason": "Vacation",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data

    def test_delete_leave_request(self, auth_client, employee, leave_type):
        request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date="2025-01-01",
            end_date="2025-01-05",
            status="PENDING",
        )
        response = auth_client.delete(
            f"/api/v1/attendance/leave-requests/{request.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
