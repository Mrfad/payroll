# Backend\clean_damage2.py
import os
import glob

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # fix the specific error
    original = content
    content = content.replace("from django.db import models
from common.models import TimeStampedModel\nimport models", "from common.models import TimeStampedModel\nfrom django.db import models")
    content = content.replace("from django.db import models
from", "from django.db import models\nfrom")
    content = content.replace("from employees.models import\n@", "@")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

for ext in ['**/*.py']:
    for f in glob.glob(ext, recursive=True):
        if 'venv' in f or '.git' in f or '__pycache__' in f: continue
        fix_file(f)
