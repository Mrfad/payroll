from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import AnonymousUser
from .models import DeviceConfiguration
import uuid

class DeviceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('X-Device-Token')
        if not token:
            return None
        
        try:
            device = DeviceConfiguration.objects.get(api_token=uuid.UUID(token), is_active=True)
        except (DeviceConfiguration.DoesNotExist, ValueError):
            raise exceptions.NotAuthenticated('Invalid or inactive device token.')
            
        request.device = device
        
        return (AnonymousUser(), device)

    def authenticate_header(self, request):
        return 'Token'
