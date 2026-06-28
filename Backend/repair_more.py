# Backend\repair_more.py
import os
import glob
import re

SERIALIZER_MAP = {
    'UserProfileSerializer': 'accounts.serializers',
    'CompanySerializer': 'companies.serializers',
    'DepartmentSerializer': 'companies.serializers',
    'EmployeeSerializer': 'employees.serializers',
    'EmployeeEnrollmentSerializer': 'employees.serializers',
    'ShiftSerializer': 'attendance.serializers',
    'BreakPolicySerializer': 'attendance.serializers',
    'OvertimePolicySerializer': 'attendance.serializers',
    'ShiftAssignmentSerializer': 'attendance.serializers',
    'AttendanceRecordSerializer': 'attendance.serializers',
    'LeaveTypeSerializer': 'attendance.serializers',
    'LeaveBalanceSerializer': 'attendance.serializers',
    'LeaveRequestSerializer': 'attendance.serializers',
    'AuditLogSerializer': 'audit.serializers',
    'SalaryComponentSerializer': 'payroll.serializers',
    'EmployeeSalaryStructureSerializer': 'payroll.serializers',
    'PayrollPeriodSerializer': 'payroll.serializers',
    'PayrollRunSerializer': 'payroll.serializers',
    'PayrollEntrySerializer': 'payroll.serializers'
}

VIEW_MAP = {
    'UserProfileViewSet': 'accounts.views',
    'CompanyViewSet': 'companies.views',
    'DepartmentViewSet': 'companies.views',
    'EmployeeViewSet': 'employees.views',
    'ShiftViewSet': 'attendance.views',
    'BreakPolicyViewSet': 'attendance.views',
    'OvertimePolicyViewSet': 'attendance.views',
    'ShiftAssignmentViewSet': 'attendance.views',
    'AttendanceRecordViewSet': 'attendance.views',
    'LeaveTypeViewSet': 'attendance.views',
    'LeaveBalanceViewSet': 'attendance.views',
    'LeaveRequestViewSet': 'attendance.views',
    'AuditLogViewSet': 'audit.views',
    'SalaryComponentViewSet': 'payroll.views',
    'EmployeeSalaryStructureViewSet': 'payroll.views',
    'PayrollPeriodViewSet': 'payroll.views',
    'PayrollRunViewSet': 'payroll.views',
    'PayrollEntryViewSet': 'payroll.views',
    'DashboardViewSet': 'payroll.views'
}

def fix_imports():
    files = glob.glob('*/tests/**/*.py', recursive=True) + glob.glob('*/views.py') + glob.glob('*/serializers.py') + glob.glob('*/urls.py') + glob.glob('*/services/**/*.py', recursive=True)
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        def replacer(m, map_dict, orig_module):
            indent = m.group(1)
            import_str = m.group(2)
            
            import_str = import_str.replace('(', '').replace(')', '').replace('\n', '')
            items = [mod.strip() for mod in import_str.split(',') if mod.strip()]
            
            new_imports = []
            for item in items:
                if item in map_dict:
                    new_imports.append(f"{indent}from {map_dict[item]} import {item}")
                else:
                    new_imports.append(f"{indent}from {orig_module} import {item}")
            
            return '\n'.join(list(set(new_imports))) # dedup
            
        new_content = content
        
        # fix serializers
        new_content = re.sub(r'^(\s*)from (?:payroll\.)?serializers import \(([^\)]+)\)', lambda m: replacer(m, SERIALIZER_MAP, 'payroll.serializers'), new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^(\s*)from (?:payroll\.)?serializers import (.*)$', lambda m: replacer(m, SERIALIZER_MAP, 'payroll.serializers'), new_content, flags=re.MULTILINE)
        
        # fix views
        new_content = re.sub(r'^(\s*)from (?:payroll\.)?views import \(([^\)]+)\)', lambda m: replacer(m, VIEW_MAP, 'payroll.views'), new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^(\s*)from (?:payroll\.)?views import (.*)$', lambda m: replacer(m, VIEW_MAP, 'payroll.views'), new_content, flags=re.MULTILINE)
        
        # also some files do 'from .serializers import *' -> I won't use regex for *. Instead, in the domains where I broke them, I explicitly used imports at the top in split_serializers and split_views.
        
        if content != new_content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)

if __name__ == '__main__':
    fix_imports()
