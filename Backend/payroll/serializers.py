# Backend\payroll\serializers.py
from accounts.models import *
from attendance.models import *
from audit.models import *
from common.models import *
from companies.models import *
from django.contrib.auth.models import Group, User
from django.db import models, transaction
from employees.models import *
from rest_framework import serializers

from payroll.models import *


class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = "__all__"


class EmployeeSalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalaryStructure
        fields = "__all__"


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = "__all__"


class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = "__all__"


class PayrollEntrySerializer(serializers.ModelSerializer):
    period_start = serializers.DateField(source="run.period.start_date", read_only=True)
    period_end = serializers.DateField(source="run.period.end_date", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = PayrollEntry
        fields = "__all__"

    def get_employee_name(self, obj):
        if obj.employee and hasattr(obj.employee, "user") and obj.employee.user:
            return (
                f"{obj.employee.user.first_name} {obj.employee.user.last_name}".strip()
                or obj.employee.user.username
            )
        return "Unknown"
