# Backend\attendance\serializers.py
from accounts.models import *
from audit.models import *
from common.models import *
from companies.models import *
from django.contrib.auth.models import Group, User
from django.db import models, transaction
from employees.models import *
from payroll.models import *
from rest_framework import serializers

from attendance.models import *


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = "__all__"


class BreakPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPolicy
        fields = "__all__"


class OvertimePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimePolicy
        fields = "__all__"


class ShiftAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAssignment
        fields = "__all__"


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_external_id = serializers.CharField(
        source="employee.employee_id", read_only=True
    )
    punched_from = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = "__all__"

    def get_punched_from(self, obj):
        devices = obj.raw_logs.values_list("device__name", flat=True).distinct()
        return ", ".join(filter(None, devices)) if devices else "Manual / Unknown"

    def get_employee_name(self, obj):
        if obj.employee and hasattr(obj.employee, "user") and obj.employee.user:
            return (
                f"{obj.employee.user.first_name} {obj.employee.user.last_name}".strip()
                or obj.employee.user.username
            )
        return "Unknown"


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = "__all__"


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = "__all__"
