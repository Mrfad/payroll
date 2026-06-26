from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from payroll.models import Employee

class Command(BaseCommand):
    help = 'Permanently removes soft-deleted employees older than a specified number of days.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after which soft-deleted employees are permanently removed (default 30)'
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"Cleaning up employees soft-deleted before {cutoff_date.date()}...")
        
        try:
            qs = Employee.objects.filter(deleted_at__lte=cutoff_date)
            count = qs.count()
            
            if count == 0:
                self.stdout.write("No employees found to clean up.")
                return

            qs.delete()
                
            self.stdout.write(self.style.SUCCESS(f"Successfully permanently deleted {count} employees."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during cleanup: {str(e)}"))
