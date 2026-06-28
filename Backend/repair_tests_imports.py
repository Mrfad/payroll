# Backend\repair_tests_imports.py
import os
import glob
import re

MODEL_MAP = {
    'TimeStampedModel': 'common.models',
    'UserProfile': 'accounts.models',
    'Company': 'companies.models',
    'Branch': 'companies.models',
    'Department': 'companies.models',
    'Shift': 'attendance.models',
    'BreakPolicy': 'attendance.models',
    'OvertimePolicy': 'attendance.models',
    'ShiftAssignment': 'attendance.models',
    'AttendanceRecord': 'attendance.models',
    'LeaveType': 'attendance.models',
    'LeaveBalance': 'attendance.models',
    'LeaveRequest': 'attendance.models',
    'Employee': 'employees.models',
    'AuditLog': 'audit.models',
    'SalaryComponent': 'payroll.models',
    'EmployeeSalaryStructure': 'payroll.models',
    'PayrollPeriod': 'payroll.models',
    'PayrollRun': 'payroll.models',
    'PayrollEntry': 'payroll.models'
}

def fix_imports():
    files = glob.glob('payroll/tests/**/*.py', recursive=True) + glob.glob('payroll/services/**/*.py', recursive=True)
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        def replacer(m):
            indent = m.group(1)
            import_str = m.group(2)
            
            # Remove parentheses and newlines
            import_str = import_str.replace('(', '').replace(')', '').replace('\n', '')
            
            # Split by comma
            models = [mod.strip() for mod in import_str.split(',') if mod.strip()]
            
            new_imports = []
            for model in models:
                if model in MODEL_MAP:
                    new_imports.append(f"{indent}from {MODEL_MAP[model]} import {model}")
                else:
                    new_imports.append(f"{indent}from payroll.models import {model}")
            
            return '\n'.join(new_imports)
            
        # Fix multiline imports
        new_content = re.sub(r'^(\s*)from payroll\.models import \(([^\)]+)\)', replacer, content, flags=re.MULTILINE)
        
        # Fix single line imports
        new_content = re.sub(r'^(\s*)from payroll\.models import (.*)$', replacer, new_content, flags=re.MULTILINE)
        
        if content != new_content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)

if __name__ == '__main__':
    fix_imports()
