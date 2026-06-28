# Backend\fix_imports.py
import os
import re
from pathlib import Path

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If file doesn't have employees.models, skip
    if 'employees.models' not in content and 'from employees import models' not in content:
        return

    # To handle this carefully, we can just find all 'from employees.models import ...'
    # and replace them. But it's easier to just do a naive approach for now:
    # 1. We will add the new imports at the top of the file.
    # 2. We will remove the words 'TimeStampedModel', 'Company', 'Department', 'UserProfile', 'AuditLog' from 'employees.models' imports.

    models_to_move = {
        'TimeStampedModel': 'common',
        'Company': 'companies',
        'Department': 'companies',
        'UserProfile': 'accounts',
        'AuditLog': 'audit',
    }

    new_imports = set()
    
    for model, app in models_to_move.items():
        if model in content:
            new_imports.add(f"from {app}.models import {model}")

    # Remove the models from employees.models imports
    for model in models_to_move.keys():
        # Replace 'Company,' with ''
        content = re.sub(r'\b' + model + r'\s*,?', '', content)
        # We might leave trailing commas or empty imports like 'from employees.models import ' or 'from employees.models import ()'

    # Cleanup empty imports
    content = re.sub(r'from employees\.models import\s*\(\s*\)', '', content)
    content = re.sub(r'from employees\.models import\s*$', '', content, flags=re.MULTILINE)
    
    # Clean up trailing commas in parens: (Employee, ) -> (Employee)
    content = re.sub(r',\s*\)', ')', content)
    # Clean up leading commas in parens: (, Employee) -> (Employee)
    content = re.sub(r'\(\s*,', '(', content)
    # Clean up double commas: ,, -> ,
    content = re.sub(r',\s*,', ',', content)
    
    # If the file imports anything, add our new imports right after the first import or at the top
    if new_imports:
        imports_str = '\n'.join(new_imports) + '\n'
        # Insert after first import, or at top
        if 'import ' in content:
            content = content.replace('import ', imports_str + 'import ', 1)
        else:
            content = imports_str + content

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    root_dir = Path('.')
    for root, dirs, files in os.walk(root_dir):
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py') and file != 'fix_imports.py':
                process_file(os.path.join(root, file))

if __name__ == '__main__':
    main()
