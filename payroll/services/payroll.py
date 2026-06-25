from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from payroll.models import (
    PayrollPeriod, PayrollRun, PayrollEntry, Employee, 
    AttendanceRecord, EmployeeSalaryStructure
)

class PayrollCalculationService:
    @staticmethod
    def calculate_payroll(period_id: int) -> PayrollRun:
        period = PayrollPeriod.objects.get(id=period_id)
        company = period.company
        
        with transaction.atomic():
            run = PayrollRun.objects.create(period=period, status='draft')
            
            employees = Employee.objects.filter(
                company=company, 
                is_active=True,
                deleted_at__isnull=True
            )
            
            for employee in employees:
                PayrollCalculationService._calculate_employee_payroll(employee, run)
                
            return run

    @staticmethod
    def _calculate_employee_payroll(employee: Employee, run: PayrollRun):
        period = run.period
        
        # Base Salary
        base_salary = employee.base_salary or Decimal('0.0')
        
        # We assume 30 days standard month for daily rate, and 8 hours for hourly rate
        # In a real system, this might be calculated based on working days in the period
        daily_rate = base_salary / Decimal('30.0') if base_salary else Decimal('0.0')
        hourly_rate = daily_rate / Decimal('8.0') if daily_rate else Decimal('0.0')
        
        details = {
            'earnings': [],
            'deductions': [],
            'attendance_summary': {
                'total_present': 0,
                'total_absent': 0,
                'total_half_day': 0,
                'total_overtime_hours': 0.0,
            }
        }
        
        gross_earnings = Decimal('0.0')
        total_deductions = Decimal('0.0')
        
        # 1. Base Salary (Earning)
        if base_salary > 0:
            gross_earnings += base_salary
            details['earnings'].append({
                'name': 'Base Salary',
                'amount': float(base_salary)
            })
            
        # 2. Add Fixed Allowances from Salary Structure
        structures = EmployeeSalaryStructure.objects.filter(
            employee=employee,
            effective_date__lte=period.end_date,
        ).exclude(end_date__lt=period.start_date)
        
        for struct in structures:
            comp = struct.component
            amount = struct.amount or Decimal('0.0')
            
            if comp.component_type == 'earning':
                gross_earnings += amount
                details['earnings'].append({
                    'name': comp.name,
                    'amount': float(amount)
                })
            else:
                total_deductions += amount
                details['deductions'].append({
                    'name': comp.name,
                    'amount': float(amount)
                })
                
        # 3. Analyze Attendance (Absences & Overtime)
        attendances = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=period.start_date,
            date__lte=period.end_date
        )
        
        absent_days = 0
        half_days = 0
        present_days = 0
        total_ot_seconds = 0
        
        for att in attendances:
            if att.status == 'absent':
                absent_days += 1
            elif att.status == 'half_day':
                half_days += 1
            elif att.status == 'present':
                present_days += 1
                
            total_ot_seconds += att.overtime_seconds
            
        details['attendance_summary']['total_absent'] = absent_days
        details['attendance_summary']['total_half_day'] = half_days
        details['attendance_summary']['total_present'] = present_days
        
        # Deduction for Absences
        if absent_days > 0:
            absence_deduction = daily_rate * Decimal(absent_days)
            total_deductions += absence_deduction
            details['deductions'].append({
                'name': f'Unpaid Absence ({absent_days} days)',
                'amount': float(absence_deduction)
            })
            
        if half_days > 0:
            # Assume a half day deducts half the daily rate
            half_day_deduction = (daily_rate / Decimal('2.0')) * Decimal(half_days)
            total_deductions += half_day_deduction
            details['deductions'].append({
                'name': f'Half Days ({half_days} days)',
                'amount': float(half_day_deduction)
            })
            
        # Earnings for Overtime
        if total_ot_seconds > 0:
            ot_hours = Decimal(total_ot_seconds) / Decimal('3600.0')
            details['attendance_summary']['total_overtime_hours'] = float(round(ot_hours, 2))
            
            # Simple assumption: 1.5x multiplier for overtime
            ot_pay = ot_hours * hourly_rate * Decimal('1.5')
            if ot_pay > 0:
                gross_earnings += ot_pay
                details['earnings'].append({
                    'name': f'Overtime ({round(ot_hours, 2)} hours)',
                    'amount': float(round(ot_pay, 2))
                })
                
        net_pay = gross_earnings - total_deductions
        
        PayrollEntry.objects.create(
            run=run,
            employee=employee,
            gross_earnings=gross_earnings,
            total_deductions=total_deductions,
            net_pay=net_pay,
            details=details
        )
