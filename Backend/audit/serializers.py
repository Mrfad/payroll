# Backend\audit\serializers.py
from accounts.models import *
from attendance.models import *
from common.models import *
from companies.models import *
from django.contrib.auth.models import Group, User
from django.db import models, transaction
from employees.models import *
from payroll.models import *
from rest_framework import serializers

from audit.models import *


class AuditLogSerializer(serializers.ModelSerializer):
    target_username = serializers.CharField(
        source="target_user.username", read_only=True
    )
    performed_by_username = serializers.CharField(
        source="performed_by.username", read_only=True
    )

    class Meta:
        model = AuditLog
        fields = "__all__"
