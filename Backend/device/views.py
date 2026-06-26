import logging

from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import DeviceTokenAuthentication
from .models import DeviceConfiguration, RawAttendanceLog
from .serializers import (
    DeviceConfigurationSerializer,
    DevicePushSerializer,
    RawAttendanceLogSerializer,
)

logger = logging.getLogger(__name__)


class IsDevice(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, "device") and request.device is not None


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
            return Response(
                {"error": "Empty payload"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = DevicePushSerializer(
            data=data, many=many, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()

            # Immediately process logs so AttendanceRecords are created
            try:
                from payroll.services.attendance import AttendanceProcessingService

                processed, failed = AttendanceProcessingService.process_pending_logs()
                if failed:
                    logger.warning(
                        f"Attendance processing: {processed} processed, {failed} failed — employee IDs may not exist"
                    )
            except Exception as e:
                logger.error(f"Attendance processing error: {e}", exc_info=True)

            return Response(
                {"status": "success", "count": len(data) if many else 1},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
