# Backend\split_urls.py
import os

DOMAINS = {
    'accounts': ['user-profile'],
    'companies': ['companies', 'departments'],
    'employees': ['employees'],
    'attendance': ['shifts', 'break-policies', 'overtime-policies', 'shift-assignments', 
                   'attendance-records', 'leave-types', 'leave-balances', 'leave-requests'],
    'audit': ['audit-logs'],
    'payroll': ['salary-components', 'employee-salary-structures', 'payroll-periods', 
                'payroll-runs', 'payroll-entries', 'dashboard']
}

VIEWSETS = {
    'user-profile': 'UserProfileViewSet',
    'companies': 'CompanyViewSet',
    'departments': 'DepartmentViewSet',
    'employees': 'EmployeeViewSet',
    'shifts': 'ShiftViewSet',
    'break-policies': 'BreakPolicyViewSet',
    'overtime-policies': 'OvertimePolicyViewSet',
    'shift-assignments': 'ShiftAssignmentViewSet',
    'attendance-records': 'AttendanceRecordViewSet',
    'leave-types': 'LeaveTypeViewSet',
    'leave-balances': 'LeaveBalanceViewSet',
    'leave-requests': 'LeaveRequestViewSet',
    'salary-components': 'SalaryComponentViewSet',
    'employee-salary-structures': 'EmployeeSalaryStructureViewSet',
    'payroll-periods': 'PayrollPeriodViewSet',
    'payroll-runs': 'PayrollRunViewSet',
    'payroll-entries': 'PayrollEntryViewSet',
    'audit-logs': 'AuditLogViewSet',
    'dashboard': 'DashboardViewSet'
}

for domain, routes in DOMAINS.items():
    if not routes: continue
    
    os.makedirs(domain, exist_ok=True)
    out_file = f"{domain}/urls.py"
    
    out_text = "from django.urls import path, include\n"
    out_text += "from rest_framework.routers import DefaultRouter\n"
    out_text += f"from .views import ({', '.join([VIEWSETS[r] for r in routes])})\n\n"
    out_text += "router = DefaultRouter()\n"
    
    for r in routes:
        if r in ['audit-logs', 'dashboard']:
            out_text += f"router.register(r'{r}', {VIEWSETS[r]}, basename='{r.replace('-', '')}')\n"
        else:
            out_text += f"router.register(r'{r}', {VIEWSETS[r]})\n"
            
    out_text += "\nurlpatterns = [\n    path('', include(router.urls)),\n]\n"
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(out_text)
    print(f"Created {out_file}")
