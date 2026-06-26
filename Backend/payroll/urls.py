from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, DepartmentViewSet, EmployeeViewSet, ShiftViewSet,
    BreakPolicyViewSet, OvertimePolicyViewSet, ShiftAssignmentViewSet,
    AttendanceRecordViewSet, LeaveTypeViewSet, LeaveBalanceViewSet,
    LeaveRequestViewSet, SalaryComponentViewSet, EmployeeSalaryStructureViewSet,
    PayrollPeriodViewSet, PayrollRunViewSet, PayrollEntryViewSet, UserProfileViewSet, AuditLogViewSet,
    DashboardViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'break-policies', BreakPolicyViewSet)
router.register(r'overtime-policies', OvertimePolicyViewSet)
router.register(r'shift-assignments', ShiftAssignmentViewSet)
router.register(r'attendance-records', AttendanceRecordViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-balances', LeaveBalanceViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'salary-components', SalaryComponentViewSet)
router.register(r'employee-salary-structures', EmployeeSalaryStructureViewSet)
router.register(r'payroll-periods', PayrollPeriodViewSet)
router.register(r'payroll-runs', PayrollRunViewSet)
router.register(r'payroll-entries', PayrollEntryViewSet)
router.register(r'user-profile', UserProfileViewSet)
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
