# Backend\attendance\views.py
from accounts.models import *
from accounts.serializers import *
from audit.models import *
from audit.serializers import *
from common.models import *
from companies.models import *
from companies.serializers import *
from django.db import transaction
from django.utils import timezone
from employees.models import *
from employees.serializers import *
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

from attendance.models import *
from attendance.serializers import *


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [DjangoModelPermissions]


class BreakPolicyViewSet(viewsets.ModelViewSet):
    queryset = BreakPolicy.objects.all()
    serializer_class = BreakPolicySerializer
    permission_classes = [DjangoModelPermissions]


class OvertimePolicyViewSet(viewsets.ModelViewSet):
    queryset = OvertimePolicy.objects.all()
    serializer_class = OvertimePolicySerializer
    permission_classes = [DjangoModelPermissions]


class ShiftAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ShiftAssignment.objects.all()
    serializer_class = ShiftAssignmentSerializer
    permission_classes = [DjangoModelPermissions]


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Employee restriction (non‑staff)
        if (not user.is_staff
            and not user.groups.filter(name__in=["Managers", "Developers"]).exists()):
            if hasattr(user, "employee"):
                qs = qs.filter(employee=user.employee)
            else:
                qs = qs.none()

        # Optional filter by employee ID
        employee_id = self.request.query_params.get("employee")
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        # --- NEW: Date range filters ---
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)

        return qs.order_by("-date", "-first_in")


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [DjangoModelPermissions]


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsOwnerOrAdmin]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsOwnerOrAdmin]
