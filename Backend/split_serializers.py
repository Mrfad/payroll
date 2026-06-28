# Backend\split_serializers.py
import os
import re

DOMAINS = {
    'accounts': ['UserProfileSerializer'],
    'companies': ['CompanySerializer', 'DepartmentSerializer'],
    'employees': ['EmployeeSerializer', 'EmployeeEnrollmentSerializer'],
    'attendance': ['ShiftSerializer', 'BreakPolicySerializer', 'OvertimePolicySerializer', 
                   'ShiftAssignmentSerializer', 'AttendanceRecordSerializer', 'LeaveTypeSerializer', 
                   'LeaveBalanceSerializer', 'LeaveRequestSerializer'],
    'audit': ['AuditLogSerializer'],
    'payroll': ['SalaryComponentSerializer', 'EmployeeSalaryStructureSerializer', 
                'PayrollPeriodSerializer', 'PayrollRunSerializer', 'PayrollEntrySerializer']
}

COMMON_IMPORTS = """from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.db import transaction, models
from common.models import *
from companies.models import *
from accounts.models import *
from employees.models import *
from attendance.models import *
from audit.models import *
from payroll.models import *
"""

with open('payroll/serializers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Split classes. We will match "class Name(" and grab until the next "class " or end of file
classes_content = {}

# Use regex to find class boundaries
class_starts = [m.start() for m in re.finditer(r'^class ', content, re.MULTILINE)]
class_starts.append(len(content))

for i in range(len(class_starts) - 1):
    start = class_starts[i]
    end = class_starts[i+1]
    cls_text = content[start:end]
    
    # Extract name
    match = re.match(r'^class (\w+)\(', cls_text)
    if match:
        name = match.group(1)
        classes_content[name] = cls_text.strip() + "\n\n"

for domain, classes in DOMAINS.items():
    if not classes: continue
    
    # ensure dir exists
    os.makedirs(domain, exist_ok=True)
    
    out_file = f"{domain}/serializers.py"
    
    # generate content
    out_text = COMMON_IMPORTS + "\n"
    
    for cls in classes:
        if cls in classes_content:
            out_text += classes_content[cls]
            
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(out_text)
        
    print(f"Wrote {len(classes)} classes to {out_file}")
