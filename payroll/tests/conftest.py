import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from payroll.models import Company, Department, Employee

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client):
    user = User.objects.create_superuser(username='admin', password='password123')
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def company():
    return Company.objects.create(name='Test Company')

@pytest.fixture
def department(company):
    return Department.objects.create(name='Test Dept', company=company)

@pytest.fixture
def employee(company, department):
    user = User.objects.create_user(username='employee_1', password='pw')
    return Employee.objects.create(user=user, company=company, department=department)
