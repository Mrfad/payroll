# Backend\companies\serializers.py
from accounts.models import *
from attendance.models import *
from audit.models import *
from common.models import *
from django.contrib.auth.models import Group, User
from django.db import models, transaction
from employees.models import *
from payroll.models import *
from rest_framework import serializers

from companies.models import *


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
