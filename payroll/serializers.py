from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.db import transaction, models
from .models import (
    Company, Department, Employee, Shift, BreakPolicy, OvertimePolicy,
    ShiftAssignment, AttendanceRecord, LeaveType, LeaveBalance, LeaveRequest,
    SalaryComponent, EmployeeSalaryStructure, PayrollPeriod, PayrollRun, PayrollEntry, UserProfile, AuditLog
)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['theme']

class AuditLogSerializer(serializers.ModelSerializer):
    target_username = serializers.CharField(source='target_user.username', read_only=True)
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

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
    employee_name = serializers.SerializerMethodField()
    employee_external_id = serializers.CharField(source='employee.employee_id', read_only=True)
    punched_from = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = '__all__'

    def get_punched_from(self, obj):
        devices = obj.raw_logs.values_list('device__name', flat=True).distinct()
        return ", ".join(filter(None, devices)) if devices else "Manual / Unknown"

    def get_employee_name(self, obj):
        if obj.employee and hasattr(obj.employee, 'user') and obj.employee.user:
            return f"{obj.employee.user.first_name} {obj.employee.user.last_name}".strip() or obj.employee.user.username
        return "Unknown"

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
    period_start = serializers.DateField(source='run.period.start_date', read_only=True)
    period_end = serializers.DateField(source='run.period.end_date', read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = PayrollEntry
        fields = '__all__'

    def get_employee_name(self, obj):
        if obj.employee and hasattr(obj.employee, 'user') and obj.employee.user:
            return f"{obj.employee.user.first_name} {obj.employee.user.last_name}".strip() or obj.employee.user.username
        return "Unknown"

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

            # 2. Add User to Employee Group
            group, _ = Group.objects.get_or_create(name='Employee')
            user.groups.add(group)

            # 3. Create Employee Profile
            employee = Employee.objects.create(user=user, **employee_data)
            
        return employee
