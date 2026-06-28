# Backend\companies\views.py
from accounts.models import *
from accounts.serializers import *
from attendance.models import *
from attendance.serializers import *
from audit.models import *
from audit.serializers import *
from common.models import *
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

from companies.models import *
from companies.models import Company, Department
from companies.serializers import *


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [DjangoModelPermissions]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [DjangoModelPermissions]
