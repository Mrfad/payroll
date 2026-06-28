# Backend\accounts\tests\test_system_views.py
import pytest
from audit.models import AuditLog
from django.contrib.auth.models import User
from rest_framework import status


@pytest.mark.django_db
class TestUserProfileViewSet:
    def test_list_user_profiles(self, auth_client):
        response = auth_client.get("/api/v1/accounts/user-profile/")
        assert response.status_code == status.HTTP_200_OK

    def test_user_profile_me_get(self, auth_client):
        response = auth_client.get("/api/v1/accounts/user-profile/me/")
        assert response.status_code == status.HTTP_200_OK
        assert "theme" in response.data

    def test_user_profile_me_patch(self, auth_client):
        # Clear existing logs to verify the new one
        AuditLog.objects.all().delete()
        response = auth_client.patch(
            "/api/v1/accounts/user-profile/me/", {"theme": "dark"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "dark"

        # Verify AuditLog was created for UserProfile
        log = AuditLog.objects.first()
        assert log is not None
        assert log.action == "UPDATE"
        assert "UserProfile" in log.details
        assert "theme changed from 'light' to 'dark'" in log.details

    def test_user_profile_me_unauthenticated(self, api_client):
        response = api_client.get("/api/v1/accounts/user-profile/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAuditLogViewSet:
    def test_list_audit_logs(self, auth_client):
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(username="admin_test", password="pw")
        AuditLog.objects.create(
            action="CREATE", target_user=user, details="Test Action"
        )
        response = auth_client.get("/api/v1/audit/audit-logs/")
        assert response.status_code == status.HTTP_200_OK

    def test_audit_log_target_user_filter(self, auth_client):
        user1 = User.objects.create_user(username="u1", password="pw")
        user2 = User.objects.create_user(username="u2", password="pw")
        AuditLog.objects.create(action="CREATE", target_user=user1, details="Log 1")
        AuditLog.objects.create(action="UPDATE", target_user=user2, details="Log 2")
        response = auth_client.get(f"/api/v1/audit/audit-logs/?target_user={user1.id}")
        assert response.status_code == status.HTTP_200_OK

        results = (
            response.data["results"] if "results" in response.data else response.data
        )
        # Depending on pagination and previous tests running, we filter by target_user.
        for r in results:
            assert r["target_user"] == user1.id

    def test_audit_log_detail(self, auth_client):
        user = User.objects.create_user(username="u3", password="pw")
        log = AuditLog.objects.create(
            action="DELETE", target_user=user, details="Delete Log"
        )
        response = auth_client.get(f"/api/v1/audit/audit-logs/{log.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == log.id

    def test_audit_log_non_manager_forbidden(self, api_client):
        user = User.objects.create_user(username="non_manager", password="pw")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/audit/audit-logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
