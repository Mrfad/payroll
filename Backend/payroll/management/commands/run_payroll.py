from django.core.management.base import BaseCommand, CommandError
from payroll.services.payroll import PayrollCalculationService
from payroll.models import PayrollPeriod

class Command(BaseCommand):
    help = 'Runs payroll calculation for a given period.'

    def add_arguments(self, parser):
        parser.add_argument('period_id', type=int, help='The ID of the PayrollPeriod to run calculation for')

    def handle(self, *args, **options):
        period_id = options['period_id']
        
        try:
            period = PayrollPeriod.objects.get(id=period_id)
        except PayrollPeriod.DoesNotExist:
            raise CommandError(f'PayrollPeriod with ID {period_id} does not exist.')

        self.stdout.write(f"Starting payroll calculation for period {period.start_date} to {period.end_date}...")
        
        try:
            run = PayrollCalculationService.calculate_payroll(period_id)
            self.stdout.write(self.style.SUCCESS(f"Successfully calculated payroll. Run ID: {run.id}"))
        except Exception as e:
            raise CommandError(f"Error calculating payroll: {str(e)}")
