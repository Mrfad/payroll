# Backend\clean_tests.py
import glob
import re

def fix_imports():
    files = glob.glob('payroll/tests/**/*.py', recursive=True)
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        def replacer(m):
            indent = m.group(1)
            return (
                f"{indent}from common.models import TimeStampedModel\n"
                f"{indent}from companies.models import Company, Branch, Department, Shift, Location\n"
                f"{indent}from accounts.models import User, Role, Permission\n"
                f"{indent}from employees.models import Employee, EmergencyContact, Document, BankAccount, EmploymentDetails\n"
                f"{indent}from attendance.models import AttendanceRecord, LeaveRequest, AttendanceRule\n"
                f"{indent}from audit.models import AuditLog\n"
                f"{indent}from payroll.models import SalaryComponent, EmployeeSalaryStructure, PayrollPeriod, PayrollRun, PayrollEntry"
            )
            
        # Fix multiline imports
        new_content = re.sub(r'^(\s*)from payroll\.models import \([^\)]+\)', replacer, content, flags=re.MULTILINE)
        
        # Fix single line imports
        new_content = re.sub(r'^(\s*)from payroll\.models import .*$', replacer, new_content, flags=re.MULTILINE)
        
        if content != new_content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
                
if __name__ == '__main__':
    fix_imports()
