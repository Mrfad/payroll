import pytest
from rest_framework import status

@pytest.mark.django_db
class TestCompanyViewSet:
    def test_list_companies(self, auth_client, company):
        response = auth_client.get('/api/v1/payroll/companies/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if 'results' in response.data else response.data
        assert len(results) >= 1

    def test_create_company(self, auth_client):
        response = auth_client.post('/api/v1/payroll/companies/', {'name': 'New Company'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Company'

    def test_delete_company(self, auth_client, company):
        response = auth_client.delete(f'/api/v1/payroll/companies/{company.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
class TestDepartmentViewSet:
    def test_list_departments(self, auth_client, department):
        response = auth_client.get('/api/v1/payroll/departments/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if 'results' in response.data else response.data
        assert len(results) >= 1

    def test_create_department(self, auth_client, company):
        response = auth_client.post('/api/v1/payroll/departments/', {
            'name': 'New Dept',
            'company': company.id
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Dept'

    def test_delete_department(self, auth_client, department):
        response = auth_client.delete(f'/api/v1/payroll/departments/{department.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
