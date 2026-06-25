from django.core.management.base import BaseCommand
from payroll.services.attendance import AttendanceProcessingService

class Command(BaseCommand):
    help = 'Processes pending raw attendance logs from devices into structured daily attendance records.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting attendance processing...")
        
        try:
            result = AttendanceProcessingService.process_pending_logs()
            
            if isinstance(result, tuple):
                processed_count, failed_count = result
            else:
                processed_count, failed_count = result, 0
                
            if processed_count > 0:
                self.stdout.write(self.style.SUCCESS(f"Successfully processed {processed_count} attendance logs."))
            if failed_count > 0:
                self.stdout.write(self.style.WARNING(f"Failed to process {failed_count} attendance logs (unknown external ID)."))
                
            if processed_count == 0 and failed_count == 0:
                self.stdout.write("No pending attendance logs to process.")
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during attendance processing: {str(e)}"))
