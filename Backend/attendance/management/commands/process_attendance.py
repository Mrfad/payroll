# Backend\attendance\management\commands\process_attendance.py
from django.core.management.base import BaseCommand

from attendance.services import AttendanceProcessingService


class Command(BaseCommand):
    help = "Processes pending attendance logs and creates attendance records."

    def handle(self, *args, **options):
        self.stdout.write("Starting attendance processing...")
        try:
            processed_count, error_count = (
                AttendanceProcessingService.process_pending_logs()
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully processed {processed_count} logs.")
            )
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(f"Failed to process {error_count} logs.")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error processing attendance: {str(e)}")
            )
