# Backend\clean_damage.py
import os

replacements = {
    r"@pytest.mark.asyncio": "@pytest.mark.asyncio",
    r"@pytest.mark.django_db": "@pytest.mark.django_db",
    r"from employees.models import Employee
@pytest.mark.django_db": "from employees.models import Employee\n@pytest.mark.django_db",
    r"# Don't create": "# Don't create",
    r"from employees.models import Employee": "from employees.models import Employee",
    r"from employees.models import Employee": "from employees.models import Employee",
    r"from employees.models import Employee": "from employees.models import Employee",
    r"from employees.models import Employee": "from employees.models import Employee",
    r"from employees.models import Employee": "from employees.models import Employee",
    r"from django.contrib.auth.models import User": "from django.contrib.auth.models import User",
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

import glob

for ext in ['**/*.py']:
    for f in glob.glob(ext, recursive=True):
        if 'venv' in f or '.git' in f or '__pycache__' in f: continue
        fix_file(f)
