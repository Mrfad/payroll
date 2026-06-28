# Backend\repair_tests.py
import os
import glob

def fix_test_files():
    for ext in ['**/*.py']:
        for filepath in glob.glob(ext, recursive=True):
            if 'venv' in filepath or '.git' in filepath or '__pycache__' in filepath: continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original = content
            # Company.objects.create missing
            content = content.replace("= Company.objects.create(name=", "= Company.objects.create(name=")
            content = content.replace("return Company.objects.create(name=", "return Company.objects.create(name=")
            content = content.replace("EmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployee.objects.all().delete()", "EmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployeeEmployee.objects.all().delete()") # Usually Employee or User in test cleanup
            content = content.replace("logs = AuditLog.objects.filter(", "logs = AuditLog.objects.filter(")
            content = content.replace("DepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartment.objects.create(company=company", "DepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartmentDepartment.objects.create(company=company")
            content = content.replace("AuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLog.objects.filter(target_user", "AuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLogAuditLog.objects.filter(target_user")
            
            # Additional imports missing
            if 'AuditLog.objects' in content and 'from audit.models import AuditLog' not in content:
                content = "from audit.models import AuditLog\n" + content
            if 'Company.objects' in content and 'from companies.models import Company' not in content:
                content = "from companies.models import Company\n" + content
            if 'Department.objects' in content and 'from companies.models import Department' not in content:
                content = "from companies.models import Department\n" + content

            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

fix_test_files()
