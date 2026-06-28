# Backend\audit\views.py
from accounts.models import *
from accounts.serializers import *
from attendance.models import *
from attendance.serializers import *
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

from audit.models import *
from audit.models import AuditLog
from audit.serializers import *


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsManagerOrDeveloper]

    def get_queryset(self):
        qs = (
            AuditLog.objects.all()
            .select_related("target_user", "performed_by")
            .order_by("-created_at")
        )
        target_user = self.request.query_params.get("target_user")
        if target_user:
            qs = qs.filter(target_user_id=target_user)
        return qs
