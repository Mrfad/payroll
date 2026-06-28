# Backend\employees\views.py
from accounts.models import *
from accounts.serializers import *
from attendance.models import *
from attendance.serializers import *
from audit.models import *
from audit.serializers import *
from common.models import *
from companies.models import *
from companies.serializers import *
from django.db import transaction
from django.utils import timezone
from payroll.models import *
from payroll.permissions import IsManagerOrDeveloper, IsOwnerOrAdmin
from payroll.serializers import *
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    DjangoModelPermissions,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.models import *
from employees.serializers import *


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "punch"]:
            return [IsAuthenticated()]
        if self.action == "enroll":
            return [IsManagerOrDeveloper()]
        return [DjangoModelPermissions()]

    def get_queryset(self):
        qs = super().get_queryset()
        show_deleted = self.request.query_params.get("show_deleted")
        if show_deleted == "true":
            qs = qs.filter(deleted_at__isnull=False)
        else:
            qs = qs.filter(deleted_at__isnull=True)

        user = self.request.user
        if (
            user.is_authenticated
            and not user.is_staff
            and not user.groups.filter(name__in=["Managers", "Developers"]).exists()
        ):
            if hasattr(user, "employee"):
                qs = qs.filter(id=user.employee.id)
            else:
                qs = qs.none()
        return qs

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request):
        serializer = EmployeeEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response(
                {
                    "message": "Employee enrolled successfully",
                    "employee_id": employee.employee_id,
                    "username": employee.user.username,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_active = instance.is_active

        diff = []
        for field, new_val in serializer.validated_data.items():
            old_val = getattr(instance, field, None)
            if hasattr(old_val, "pk"):
                old_val = str(old_val)
            if hasattr(new_val, "pk"):
                new_val = str(new_val)
            if str(old_val) != str(new_val):
                diff.append(f"{field} changed from '{old_val}' to '{new_val}'")

        employee = serializer.save()
        new_active = employee.is_active

        action = "UPDATE"
        if old_active and not new_active:
            action = "FREEZE"
        elif not old_active and new_active:
            action = "UNFREEZE"

        details_text = f"Updated employee {employee.employee_id}."
        if diff:
            details_text += " Changes: " + "; ".join(diff)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def punch(self, request, pk=None):
        employee = self.get_object()
        direction = request.data.get("direction", None)

        from device.models import DeviceConfiguration, RawAttendanceLog
        from django.utils import timezone

        # Get or create a dummy device for app punches
        device, _ = DeviceConfiguration.objects.get_or_create(
            name="App Punch",
            device_type="app",
            company=employee.company,
            defaults={"api_token": "00000000-0000-0000-0000-000000000000"},
        )

        RawAttendanceLog.objects.create(
            device=device,
            external_id=str(
                employee.employee_id if employee.employee_id else employee.id
            ),
            punch_time=timezone.now(),
            direction=direction,
            raw_data={"source": "app_punch"},
        )

        from attendance.services import AttendanceProcessingService

        AttendanceProcessingService.process_pending_logs()

        return Response(
            {"status": "Punch recorded successfully"}, status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save()

        user = instance.user
        user.is_active = False
        user.save()

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.deleted_at = None
        instance.is_active = True
        instance.save()

        user = instance.user
        user.is_active = True
        user.save()
        return Response({"status": "restored"})
