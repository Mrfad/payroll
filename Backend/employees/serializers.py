# Backend\employees\serializers.py
from accounts.models import *
from attendance.models import *
from audit.models import *
from common.models import *
from companies.models import *
from companies.models import Company, Department
from django.contrib.auth.models import Group, User
from django.db import models, transaction
from payroll.models import *
from rest_framework import serializers

from employees.models import *


class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "user" in self.fields:
            # If editing an existing single employee, include their current user account in the dropdown
            if hasattr(self.instance, "user_id"):
                self.fields["user"].queryset = User.objects.filter(
                    models.Q(employee__isnull=True) | models.Q(pk=self.instance.user_id)
                )
            # If creating a new employee or serializing a list, only show users without an employee profile
            else:
                self.fields["user"].queryset = User.objects.filter(
                    employee__isnull=True
                )


class EmployeeEnrollmentSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    hire_date = serializers.DateField(required=False, allow_null=True)

    # Employee fields
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True
    )
    employee_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    designation = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    base_salary = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True
    )

    def create(self, validated_data):
        user_data = {
            "username": validated_data.get("username"),
            "email": validated_data.get("email"),
            "first_name": validated_data.get("first_name", ""),
            "last_name": validated_data.get("last_name", ""),
        }
        password = validated_data.get("password")

        employee_data = {
            "company": validated_data.get("company"),
            "department": validated_data.get("department"),
            "employee_id": validated_data.get("employee_id"),
            "designation": validated_data.get("designation", ""),
            "phone": validated_data.get("phone", ""),
            "base_salary": validated_data.get("base_salary"),
            'hire_date': validated_data.get('hire_date'),
        }

        with transaction.atomic():
            # 1. Create User
            user = User(**user_data)
            user.set_password(password)
            user.save()

            # 2. Add User to Employee Group
            group, _ = Group.objects.get_or_create(name="Employee")
            user.groups.add(group)

            # 3. Create Employee Profile
            employee = Employee.objects.create(user=user, **employee_data)

        return employee
