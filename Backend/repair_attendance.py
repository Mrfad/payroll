# Backend\repair_attendance.py
import os

def fix_attendance_models():
    filepath = 'attendance/models.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace("class Shift():", "class Shift(TimeStampedModel):")
    content = content.replace("class BreakPolicy():", "class BreakPolicy(TimeStampedModel):")
    content = content.replace("class OvertimePolicy():", "class OvertimePolicy(TimeStampedModel):")
    content = content.replace("class ShiftAssignment():", "class ShiftAssignment(TimeStampedModel):")
    content = content.replace("class AttendanceRecord():", "class AttendanceRecord(TimeStampedModel):")
    content = content.replace("class LeaveType():", "class LeaveType(TimeStampedModel):")
    content = content.replace("class LeaveBalance():", "class LeaveBalance(TimeStampedModel):")
    content = content.replace("class LeaveRequest():", "class LeaveRequest(TimeStampedModel):")
    content = content.replace("models.ForeignKey( on_delete=models.CASCADE)", "models.ForeignKey(Company, on_delete=models.CASCADE)")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_attendance_models()
