# Backend\payroll\views.py
from datetime import date, timedelta

from accounts.models import *
from accounts.serializers import *
from attendance.models import *
from attendance.serializers import *
from audit.models import *
from audit.models import AuditLog
from audit.serializers import *
from common.models import *
from companies.models import *
from companies.models import Department
from companies.serializers import *
from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from employees.models import *
from employees.serializers import *
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

from payroll.models import *
from payroll.permissions import IsManagerOrDeveloper, IsOwnerOrAdmin
from payroll.serializers import *


class SalaryComponentViewSet(viewsets.ModelViewSet):
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    permission_classes = [DjangoModelPermissions]


class EmployeeSalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalaryStructure.objects.all()
    serializer_class = EmployeeSalaryStructureSerializer
    permission_classes = [IsOwnerOrAdmin]


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [DjangoModelPermissions]


class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [DjangoModelPermissions]


class PayrollEntryViewSet(viewsets.ModelViewSet):
    queryset = PayrollEntry.objects.all()
    serializer_class = PayrollEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if (
            not user.is_staff
            and not user.groups.filter(name__in=["Managers", "Developers"]).exists()
        ):
            if hasattr(user, "employee"):
                qs = qs.filter(employee=user.employee)
            else:
                qs = qs.none()

        employee_id = self.request.query_params.get("employee")
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        return qs.order_by("-run__period__start_date")


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Employee.objects.none()  # Needed for DjangoModelPermissions to work on ViewSet sometimes, or just use AllowAny/IsAuthenticated

    def list(self, request):
        total_employees = Employee.objects.filter(
            is_active=True, deleted_at__isnull=True
        ).count()

        latest_run = PayrollRun.objects.order_by("-created_at").first()
        active_payroll = 0
        if latest_run:
            agg = PayrollEntry.objects.filter(run=latest_run).aggregate(
                total=Sum("net_pay")
            )
            active_payroll = agg["total"] or 0

        pending_requests = LeaveRequest.objects.filter(status="pending").count()

        today = date.today()
        present_today = AttendanceRecord.objects.filter(
            date=today, status="present"
        ).count()
        attendance_percentage = (
            (present_today / total_employees * 100) if total_employees > 0 else 0
        )

        dept_distribution = Department.objects.annotate(
            employee_count=Count("employee")
        ).values("name", "employee_count")

        recent_activity = AuditLogSerializer(
            AuditLog.objects.select_related("target_user", "performed_by").order_by(
                "-created_at"
            )[:5],
            many=True,
        ).data

        return Response(
            {
                "total_employees": total_employees,
                "active_payroll": active_payroll,
                "pending_requests": pending_requests,
                "attendance_percentage": round(attendance_percentage, 1),
                "department_distribution": list(dept_distribution),
                "recent_activity": recent_activity,
                "monthly_trend": [  # Mock data for now
                    {"month": "Jan", "amount": 3500000},
                    {"month": "Feb", "amount": 4000000},
                    {"month": "Mar", "amount": 3800000},
                    {"month": "Apr", "amount": 5000000},
                    {"month": "May", "amount": 4800000},
                    {"month": "Jun", "amount": 6200000},
                ],
            }
        )
