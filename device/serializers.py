from rest_framework import serializers
from .models import DeviceConfiguration, RawAttendanceLog

class DeviceConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceConfiguration
        exclude = ['api_token']

class RawAttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawAttendanceLog
        fields = '__all__'

class DevicePushSerializer(serializers.Serializer):
    external_id = serializers.CharField(max_length=255)
    punch_time = serializers.DateTimeField()
    direction = serializers.ChoiceField(choices=[('in','In'),('out','Out')], required=False, allow_null=True)
    
    def create(self, validated_data):
        device = self.context['request'].device
        
        # Make a copy of validated data for raw_data JSON storage (casting datetime to str)
        raw_payload = dict(validated_data)
        raw_payload['punch_time'] = raw_payload['punch_time'].isoformat()

        return RawAttendanceLog.objects.create(
            device=device,
            external_id=validated_data['external_id'],
            punch_time=validated_data['punch_time'],
            direction=validated_data.get('direction'),
            raw_data=raw_payload,
            status='pending'
        )
