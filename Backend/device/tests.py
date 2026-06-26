import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from payroll.models import Company
from device.models import DeviceConfiguration, RawAttendanceLog
from django.utils.timezone import now

@pytest.fixture
def auth_client():
    user = User.objects.create_superuser(username='device_admin', password='password123')
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def company():
    return Company.objects.create(name='Device Test Company')

@pytest.fixture
def device_config(company):
    return DeviceConfiguration.objects.create(name='Test Device', device_type='zkteco', company=company)

@pytest.mark.django_db
class TestDeviceConfigurationViewSet:
    def test_list_device_configs(self, auth_client, device_config):
        response = auth_client.get('/api/v1/device/configurations/')
        assert response.status_code == status.HTTP_200_OK
        data_to_check = response.data['results'][0] if 'results' in response.data else response.data[0]
        assert 'api_token' not in data_to_check

    def test_create_device_config(self, auth_client, company):
        response = auth_client.post('/api/v1/device/configurations/', {
            'name': 'New Device',
            'device_type': 'faceapi',
            'company': company.id
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_device_config(self, auth_client, device_config):
        response = auth_client.patch(f'/api/v1/device/configurations/{device_config.id}/', {
            'name': 'Updated Device'
        })
        assert response.status_code == status.HTTP_200_OK

    def test_delete_device_config(self, auth_client, device_config):
        response = auth_client.delete(f'/api/v1/device/configurations/{device_config.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
class TestRawAttendanceLogViewSet:
    def test_list_raw_logs(self, auth_client, device_config):
        RawAttendanceLog.objects.create(
            device=device_config, external_id='E001', punch_time=now(), raw_data={}
        )
        response = auth_client.get('/api/v1/device/raw-logs/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_raw_log(self, auth_client, device_config):
        response = auth_client.post('/api/v1/device/raw-logs/', {
            'device': device_config.id,
            'external_id': 'E002',
            'punch_time': now().isoformat(),
            'raw_data': {}
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
class TestDevicePushView:
    def test_push_single_valid_punch(self, device_config):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN=str(device_config.api_token))
        response = client.post('/api/v1/device/push/', {
            "external_id": "EMP-001",
            "punch_time": now().isoformat(),
            "direction": "in"
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert RawAttendanceLog.objects.filter(device=device_config).count() == 1

    def test_push_unauthenticated(self):
        client = APIClient()
        response = client.post('/api/v1/device/push/', {
            "external_id": "EMP-001",
            "punch_time": now().isoformat()
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_push_batch_punches(self, device_config):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN=str(device_config.api_token))
        payload = [
            {"external_id": "E1", "punch_time": now().isoformat()},
            {"external_id": "E2", "punch_time": now().isoformat()},
            {"external_id": "E3", "punch_time": now().isoformat()}
        ]
        response = client.post('/api/v1/device/push/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert RawAttendanceLog.objects.count() == 3

    def test_push_missing_external_id(self, device_config):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN=str(device_config.api_token))
        response = client.post('/api/v1/device/push/', {"direction": "in"}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_push_invalid_date(self, device_config):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN=str(device_config.api_token))
        response = client.post('/api/v1/device/push/', {"external_id":"E1","punch_time":"bad"}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_push_inactive_device(self, device_config):
        device_config.is_active = False
        device_config.save()
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN=str(device_config.api_token))
        response = client.post('/api/v1/device/push/', {"external_id": "E1", "punch_time": now().isoformat()}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_push_invalid_token(self):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN="not-a-uuid")
        response = client.post('/api/v1/device/push/', {"external_id": "E1", "punch_time": now().isoformat()}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_push_empty_dict(self, device_config):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN=str(device_config.api_token))
        response = client.post('/api/v1/device/push/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_push_empty_array(self, device_config):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_TOKEN=str(device_config.api_token))
        response = client.post('/api/v1/device/push/', [], format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
