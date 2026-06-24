from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import DeviceConfiguration, RawAttendanceLog
from .serializers import DeviceConfigurationSerializer, RawAttendanceLogSerializer

class DeviceConfigurationViewSet(viewsets.ModelViewSet):
    queryset = DeviceConfiguration.objects.all()
    serializer_class = DeviceConfigurationSerializer
    permission_classes = [IsAdminUser]

class RawAttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = RawAttendanceLog.objects.all()
    serializer_class = RawAttendanceLogSerializer
    permission_classes = [IsAdminUser]
