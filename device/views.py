from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, BasePermission
from .models import DeviceConfiguration, RawAttendanceLog
from .serializers import DeviceConfigurationSerializer, RawAttendanceLogSerializer, DevicePushSerializer
from .authentication import DeviceTokenAuthentication

class IsDevice(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'device') and request.device is not None

class DeviceConfigurationViewSet(viewsets.ModelViewSet):
    queryset = DeviceConfiguration.objects.all()
    serializer_class = DeviceConfigurationSerializer
    permission_classes = [IsAdminUser]

class RawAttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = RawAttendanceLog.objects.all()
    serializer_class = RawAttendanceLogSerializer
    permission_classes = [IsAdminUser]

class DevicePushView(APIView):
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [IsDevice]

    def post(self, request):
        data = request.data
        many = isinstance(data, list)
        
        if many and len(data) == 0:
            return Response({"error": "Empty payload"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DevicePushSerializer(data=data, many=many, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            
            # Immediately process logs so UI updates
            try:
                from payroll.services.attendance import AttendanceProcessingService
                AttendanceProcessingService.process_pending_logs()
            except Exception as e:
                pass # Don't fail the push if processing fails
                
            return Response({"status": "success", "count": len(data) if many else 1}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
