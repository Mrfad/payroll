# Backend\split_views.py
import os
import re

DOMAINS = {
    'accounts': ['UserProfileViewSet'],
    'companies': ['CompanyViewSet', 'DepartmentViewSet'],
    'employees': ['EmployeeViewSet'],
    'attendance': ['ShiftViewSet', 'BreakPolicyViewSet', 'OvertimePolicyViewSet', 
                   'ShiftAssignmentViewSet', 'AttendanceRecordViewSet', 'LeaveTypeViewSet', 
                   'LeaveBalanceViewSet', 'LeaveRequestViewSet'],
    'audit': ['AuditLogViewSet'],
    'payroll': ['SalaryComponentViewSet', 'EmployeeSalaryStructureViewSet', 
                'PayrollPeriodViewSet', 'PayrollRunViewSet', 'PayrollEntryViewSet', 'DashboardViewSet']
}

COMMON_IMPORTS = """from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAdminUser, AllowAny, DjangoModelPermissions, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils import timezone
from django.db import transaction

from common.models import *
from companies.models import *
from accounts.models import *
from employees.models import *
from attendance.models import *
from audit.models import *
from payroll.models import *

from companies.serializers import *
from accounts.serializers import *
from employees.serializers import *
from attendance.serializers import *
from audit.serializers import *
from payroll.serializers import *

from payroll.permissions import IsManagerOrDeveloper, IsOwnerOrAdmin
"""

with open('payroll/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

classes_content = {}
class_starts = [m.start() for m in re.finditer(r'^class ', content, re.MULTILINE)]
class_starts.append(len(content))

for i in range(len(class_starts) - 1):
    start = class_starts[i]
    end = class_starts[i+1]
    cls_text = content[start:end]
    
    match = re.match(r'^class (\w+)\(', cls_text)
    if match:
        name = match.group(1)
        classes_content[name] = cls_text.strip() + "\n\n"

for domain, classes in DOMAINS.items():
    if not classes: continue
    
    os.makedirs(domain, exist_ok=True)
    out_file = f"{domain}/views.py"
    
    out_text = COMMON_IMPORTS + "\n"
    
    for cls in classes:
        if cls in classes_content:
            out_text += classes_content[cls]
            
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(out_text)
        
    print(f"Wrote {len(classes)} classes to {out_file}")
