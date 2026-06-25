import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from payroll.models import Employee, AuditLog

class Command(BaseCommand):
    help = 'Hard deletes employees that have been soft-deleted for more than 1 year (365 days)'

    def handle(self, *args, **kwargs):
        one_year_ago = timezone.now() - datetime.timedelta(days=365)
        
        employees_to_delete = Employee.objects.filter(deleted_at__lt=one_year_ago)
        count = employees_to_delete.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No employees to permanently delete.'))
            return
            
        for emp in employees_to_delete:
            AuditLog.objects.create(
                action='HARD_DELETE',
                target_user=emp.user,
                performed_by=None,
                details=f"System automatically permanently deleted employee {emp.employee_id} after 1 year retention."
            )
            # Hard delete the employee
            # The User is also deleted via models.CASCADE
            emp.user.delete()
            
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} employees.'))
