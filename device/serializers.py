from rest_framework import serializers
from .models import DeviceConfiguration, RawAttendanceLog

class DeviceConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceConfiguration
        fields = '__all__'

class RawAttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawAttendanceLog
        fields = '__all__'
