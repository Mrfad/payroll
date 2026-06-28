# Backend\payroll\admin.py
from accounts.models import *
from attendance.models import *
from audit.models import *
from common.models import *
from companies.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from employees.models import *

from .models import (
    EmployeeSalaryStructure,
    PayrollEntry,
    PayrollPeriod,
    PayrollRun,
    SalaryComponent,
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "theme")
    search_fields = ("user__username",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "parent")
    list_filter = ("company",)
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "employee_id",
        "company",
        "department",
        "designation",
        "is_active",
    )
    list_filter = ("company", "department", "is_active")
    search_fields = ("user__username", "employee_id", "phone", "designation")


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "start_time", "end_time")
    list_filter = ("company",)


@admin.register(BreakPolicy)
class BreakPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "is_paid")
    list_filter = ("company", "is_paid")


@admin.register(OvertimePolicy)
class OvertimePolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "rate_multiplier")


@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ("employee", "shift", "start_date", "end_date")
    list_filter = ("shift", "start_date")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "status", "first_in", "last_out")
    list_filter = ("status", "date")
    search_fields = ("employee__user__username", "employee__employee_id")


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "is_paid")


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "current_balance")
    search_fields = ("employee__user__username",)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "status")
    list_filter = ("status", "leave_type")


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "component_type", "calculation_method")
    list_filter = ("company", "component_type")


@admin.register(EmployeeSalaryStructure)
class EmployeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = ("employee", "component", "amount", "effective_date")


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ("company", "start_date", "end_date", "status")
    list_filter = ("status", "company")


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ("period", "run_date", "status")
    list_filter = ("status",)


@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ("run", "employee", "net_pay")
    list_filter = ("run",)
    list_select_related = ("run__period", "employee__user")
