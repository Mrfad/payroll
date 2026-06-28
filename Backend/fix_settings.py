# Backend\fix_settings.py
import re

with open('prj/settings.py', 'r') as f:
    content = f.read()

apps_block = """INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'common',
    'accounts',
    'companies',
    'employees',
    'attendance',
    'payroll',
    'device',
    'audit',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
]"""

# Replace the INSTALLED_APPS block
content = re.sub(r'INSTALLED_APPS = \[.*?\]', apps_block, content, flags=re.DOTALL)

with open('prj/settings.py', 'w') as f:
    f.write(content)
