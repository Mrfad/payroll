import pytest
from rest_framework import status
from payroll.models import Company

@pytest.mark.django_db
class TestPagination:
    def test_pagination_format(self, auth_client):
        for i in range(15):
            Company.objects.create(name=f'Company {i}')
        
        response = auth_client.get('/api/v1/payroll/companies/')
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        assert len(response.data['results']) <= 100
