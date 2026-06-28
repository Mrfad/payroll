# Backend\attendance\tests\test_shift_views.py
import pytest
from rest_framework import status

from attendance.models import BreakPolicy, OvertimePolicy, Shift, ShiftAssignment


@pytest.fixture
def shift(company):
    return Shift.objects.create(
        name="Morning", company=company, start_time="09:00:00", end_time="17:00:00"
    )


@pytest.fixture
def break_policy(company):
    return BreakPolicy.objects.create(
        name="Standard Break", company=company, duration_minutes=60
    )


@pytest.fixture
def overtime_policy(company):
    return OvertimePolicy.objects.create(
        name="Standard OT",
        company=company,
        rate_multiplier=1.5,
        daily_threshold_hours=8,
    )


@pytest.mark.django_db
class TestShiftViewSet:
    def test_list_shifts(self, auth_client, shift):
        response = auth_client.get("/api/v1/attendance/shifts/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_shift(self, auth_client, company):
        response = auth_client.post(
            "/api/v1/attendance/shifts/",
            {
                "name": "Night",
                "company": company.id,
                "start_time": "20:00:00",
                "end_time": "04:00:00",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_shift(self, auth_client, shift):
        response = auth_client.delete(f"/api/v1/attendance/shifts/{shift.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestBreakPolicyViewSet:
    def test_list_break_policies(self, auth_client, break_policy):
        response = auth_client.get("/api/v1/attendance/break-policies/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_break_policy(self, auth_client, company):
        response = auth_client.post(
            "/api/v1/attendance/break-policies/",
            {"name": "Short Break", "company": company.id, "duration_minutes": 15},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_break_policy(self, auth_client, break_policy):
        response = auth_client.delete(
            f"/api/v1/attendance/break-policies/{break_policy.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestOvertimePolicyViewSet:
    def test_list_overtime_policies(self, auth_client, overtime_policy):
        response = auth_client.get("/api/v1/attendance/overtime-policies/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_overtime_policy(self, auth_client, company):
        response = auth_client.post(
            "/api/v1/attendance/overtime-policies/",
            {
                "name": "Double OT",
                "company": company.id,
                "rate_multiplier": 2.0,
                "daily_threshold_hours": 10,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_overtime_policy(self, auth_client, overtime_policy):
        response = auth_client.delete(
            f"/api/v1/attendance/overtime-policies/{overtime_policy.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestShiftAssignmentViewSet:
    def test_list_shift_assignments(self, auth_client, employee, shift):
        ShiftAssignment.objects.create(
            employee=employee, shift=shift, start_date="2025-01-01"
        )
        response = auth_client.get("/api/v1/attendance/shift-assignments/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_shift_assignment(self, auth_client, employee, shift):
        response = auth_client.post(
            "/api/v1/attendance/shift-assignments/",
            {"employee": employee.id, "shift": shift.id, "start_date": "2025-02-01"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_shift_assignment(self, auth_client, employee, shift):
        assignment = ShiftAssignment.objects.create(
            employee=employee, shift=shift, start_date="2025-01-01"
        )
        response = auth_client.delete(
            f"/api/v1/attendance/shift-assignments/{assignment.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
