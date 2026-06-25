from django.core.management.base import BaseCommand
from payroll.models import PayrollPeriod
from payroll.services.payroll import PayrollCalculationService

class Command(BaseCommand):
    help = 'Run payroll calculation for a given payroll period.'

    def add_arguments(self, parser):
        parser.add_argument('--period-id', type=int, required=True, help='ID of the PayrollPeriod to run calculation for')

    def handle(self, *args, **options):
        period_id = options['period_id']
        
        try:
            period = PayrollPeriod.objects.get(id=period_id)
        except PayrollPeriod.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"PayrollPeriod with ID {period_id} does not exist."))
            return

        self.stdout.write(f"Starting payroll calculation for period: {period.start_date} to {period.end_date}...")
        
        try:
            run = PayrollCalculationService.calculate_payroll(period_id)
            self.stdout.write(self.style.SUCCESS(f"Successfully ran payroll (Run ID: {run.id})"))
            self.stdout.write(f"Created {run.entries.count()} payslip entries.")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to calculate payroll: {str(e)}"))
