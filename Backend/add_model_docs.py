# Backend\add_model_docs.py
import os
import glob
import re

DOCSTRINGS = {
    'TimeStampedModel': '"""\n    Abstract base model that provides self-updating `created_at` and `updated_at` fields.\n    All other models should inherit from this to ensure consistent timestamp tracking.\n    """',
    'Company': '"""\n    Represents a tenant or organization within the platform.\n    All other entities (employees, departments, etc.) are linked to a Company to ensure data isolation.\n    """',
    'Branch': '"""\n    Represents a physical location or subsidiary of a Company.\n    Useful for organizations with multiple offices or distinct regional entities.\n    """',
    'Department': '"""\n    Represents a functional division within a Company (e.g., HR, IT, Finance).\n    Employees are assigned to departments for organizational structuring.\n    """',
    'UserProfile': '"""\n    Extends the default Django User model with application-specific preferences and roles.\n    Connects authentication details to the core Employee entity.\n    """',
    'Employee': '"""\n    The central entity of the system representing a person working for a Company.\n    Stores personal information, employment details, and serves as the anchor for payroll and attendance.\n    """',
    'Shift': '"""\n    Defines a standard working schedule (e.g., 9 AM to 5 PM).\n    Used to evaluate employee attendance, lateness, and overtime.\n    """',
    'BreakPolicy': '"""\n    Defines rules for employee breaks during a Shift (e.g., 1 hour lunch break).\n    Used to calculate net working hours and deduct unpaid break times.\n    """',
    'OvertimePolicy': '"""\n    Defines rules and rates for calculating overtime pay.\n    Determines how hours worked beyond the standard shift are compensated.\n    """',
    'ShiftAssignment': '"""\n    Maps an Employee to a specific Shift.\n    Allows for flexible scheduling where employees might have different shifts on different days.\n    """',
    'AttendanceRecord': '"""\n    Records an employee\'s daily attendance, including clock-in and clock-out times.\n    Used by the payroll calculation engine to determine hours worked and absences.\n    """',
    'LeaveType': '"""\n    Defines categories of time off (e.g., Annual Leave, Sick Leave).\n    Determines whether the leave is paid or unpaid and the default accrual rules.\n    """',
    'LeaveBalance': '"""\n    Tracks the amount of leave an employee has accrued and taken for a specific LeaveType.\n    Ensures employees do not exceed their allowed time off.\n    """',
    'LeaveRequest': '"""\n    Represents an employee\'s application for time off.\n    Tracks the approval workflow (pending, approved, rejected) and dates requested.\n    """',
    'AuditLog': '"""\n    Maintains an immutable record of significant actions within the system.\n    Tracks who made what changes (create, update, delete) to which records for compliance.\n    """',
    'SalaryComponent': '"""\n    Defines individual parts of a salary (e.g., Basic Pay, Housing Allowance, Tax Deduction).\n    Components can be earnings or deductions and are used to construct a salary structure.\n    """',
    'EmployeeSalaryStructure': '"""\n    Maps a SalaryComponent to a specific Employee with an assigned monetary amount.\n    Represents the employee\'s individualized compensation package.\n    """',
    'PayrollPeriod': '"""\n    Defines a specific time frame (e.g., January 2026) for which payroll is calculated.\n    Groups all payroll runs and attendance records for a specific cycle.\n    """',
    'PayrollRun': '"""\n    Represents the execution of a payroll calculation for a specific Employee in a PayrollPeriod.\n    Stores the finalized gross pay, total deductions, and net pay.\n    """',
    'PayrollEntry': '"""\n    Stores the detailed breakdown of a PayrollRun (line items).\n    Records the exact amount for each SalaryComponent during that specific payroll cycle.\n    """'
}

def add_docstrings():
    for app in ['common', 'companies', 'accounts', 'employees', 'attendance', 'audit', 'payroll']:
        filepath = f"{app}/models.py"
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for model_name, docstring in DOCSTRINGS.items():
            # Regex to find class definition that doesn't already have a docstring
            # Looks for: class ModelName(args):
            pattern = r'(class\s+' + model_name + r'\([^)]*\):(?:\s*))(?!""")'
            
            # Replace by adding the docstring
            def replacer(match):
                return f"{match.group(1)}{docstring}\n"
                
            content = re.sub(pattern, replacer, content)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    add_docstrings()
