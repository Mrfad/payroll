# Backend\fix_test_urls.py
import os
import glob
import re

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

def fix_urls():
    files = glob.glob('*/tests/**/*.py', recursive=True) + glob.glob('payroll/tests/**/*.py', recursive=True)
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        new_content = content
        
        for domain, routes in DOMAINS.items():
            for route in routes:
                # Replace exact paths, e.g., /api/v1/payroll/companies/ -> /api/v1/companies/companies/
                # Note: some have trailing slash, some have pk.
                new_content = re.sub(
                    rf'/api/v1/payroll/{route}/',
                    f'/api/v1/{domain}/{route}/',
                    new_content
                )
                
        if content != new_content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Fixed URLs in {f}")

if __name__ == '__main__':
    fix_urls()
