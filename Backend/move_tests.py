# Backend\move_tests.py
import os
import shutil

moves = [
    ('payroll/tests/test_auth.py', 'accounts/tests/test_auth.py'),
    ('payroll/tests/test_permissions.py', 'accounts/tests/test_permissions.py'),
    ('payroll/tests/test_system_views.py', 'accounts/tests/test_system_views.py'),
    ('payroll/tests/test_reference_views.py', 'companies/tests/test_reference_views.py'),
    ('payroll/tests/test_attendance_processing.py', 'attendance/tests/test_attendance_processing.py'),
    ('payroll/tests/test_attendance_views.py', 'attendance/tests/test_attendance_views.py'),
    ('payroll/tests/test_shift_views.py', 'attendance/tests/test_shift_views.py'),
]

for src, dst in moves:
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        # ensure __init__.py exists
        init_file = os.path.join(os.path.dirname(dst), '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()
            
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")
    else:
        print(f"Warning: {src} not found")
