# Backend\accounts\tests\test_auth.py
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def auth_user():
    return User.objects.create_user(username="test_user", password="password123")


@pytest.mark.django_db
class TestAuthEndpoints:
    def test_token_obtain_pair(self, api_client, auth_user):
        url = reverse("token_obtain_pair")
        response = api_client.post(
            url, {"username": "test_user", "password": "password123"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_token_refresh(self, api_client, auth_user):
        obtain_url = reverse("token_obtain_pair")
        response = api_client.post(
            obtain_url,
            {"username": "test_user", "password": "password123"},
            format="json",
        )
        refresh_token = response.data["refresh"]

        refresh_url = reverse("token_refresh")
        response = api_client.post(
            refresh_url, {"refresh": refresh_token}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_token_verify(self, api_client, auth_user):
        obtain_url = reverse("token_obtain_pair")
        response = api_client.post(
            obtain_url,
            {"username": "test_user", "password": "password123"},
            format="json",
        )
        access_token = response.data["access"]

        verify_url = reverse("token_verify")
        response = api_client.post(verify_url, {"token": access_token}, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_token_blacklist(self, api_client, auth_user):
        obtain_url = reverse("token_obtain_pair")
        response = api_client.post(
            obtain_url,
            {"username": "test_user", "password": "password123"},
            format="json",
        )
        refresh_token = response.data["refresh"]

        blacklist_url = reverse("token_blacklist")
        response = api_client.post(
            blacklist_url, {"refresh": refresh_token}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
