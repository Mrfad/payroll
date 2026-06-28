# Backend\check_damage.py
import re
import os
from pathlib import Path

def fix_messed_up_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The bad script removed 'Company,' 'Department,' 'UserProfile,' 'AuditLog,' 'TimeStampedModel,'
    # and replaced them with empty strings, leaving weird artifacts.
    # For instance '@pytest.mark.asyncio'
    # Originally it was probably:
    # from employees.models import Company, Employee
    # @pytest.mark.asyncio

    # Since there are very few files, I'll print the affected lines first to see the damage
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'employees.models' in line:
            print(f"{filepath}:{i+1} -> {line}")

root_dir = Path('.')
for root, dirs, files in os.walk(root_dir):
    if 'venv' in root or '.git' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            fix_messed_up_file(os.path.join(root, file))
