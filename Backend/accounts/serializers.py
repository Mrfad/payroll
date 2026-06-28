# Backend\accounts\serializers.py
from attendance.models import *
from audit.models import *
from common.models import *
from companies.models import *
from django.contrib.auth.models import Group, User
from django.db import models, transaction
from employees.models import *
from payroll.models import *
from rest_framework import serializers

from accounts.models import *


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["theme"]
