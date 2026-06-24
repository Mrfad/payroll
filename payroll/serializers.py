from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction, models
from .models import (
    Company, Department, Employee, Shift, BreakPolicy, OvertimePolicy,
    ShiftAssignment, AttendanceRecord, LeaveType, LeaveBalance, LeaveRequest,
    SalaryComponent, EmployeeSalaryStructure, PayrollPeriod, PayrollRun, PayrollEntry
)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            # If editing an existing single employee, include their current user account in the dropdown
            if hasattr(self.instance, 'user_id'):
                self.fields['user'].queryset = User.objects.filter(
                    models.Q(employee__isnull=True) | models.Q(pk=self.instance.user_id)
                )
            # If creating a new employee or serializing a list, only show users without an employee profile
            else:
                self.fields['user'].queryset = User.objects.filter(employee__isnull=True)

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'

class BreakPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPolicy
        fields = '__all__'

class OvertimePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimePolicy
        fields = '__all__'

class ShiftAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAssignment
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'

class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = '__all__'

class EmployeeSalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalaryStructure
        fields = '__all__'

class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'

class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = '__all__'

class PayrollEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollEntry
        fields = '__all__'

class EmployeeEnrollmentSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    # Employee fields
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False, allow_null=True)
    employee_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    designation = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    base_salary = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    def create(self, validated_data):
        user_data = {
            'username': validated_data.get('username'),
            'email': validated_data.get('email'),
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', '')
        }
        password = validated_data.get('password')
        
        employee_data = {
            'company': validated_data.get('company'),
            'department': validated_data.get('department'),
            'employee_id': validated_data.get('employee_id'),
            'designation': validated_data.get('designation', ''),
            'phone': validated_data.get('phone', ''),
            'base_salary': validated_data.get('base_salary')
        }

        with transaction.atomic():
            # 1. Create User
            user = User(**user_data)
            user.set_password(password)
            user.save()

            # 2. Create Employee Profile
            employee = Employee.objects.create(user=user, **employee_data)
            
        return employee
