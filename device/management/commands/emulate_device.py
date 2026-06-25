import random
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from device.models import DeviceConfiguration
from payroll.models import Company, Employee

class Command(BaseCommand):
    help = 'Emulate an attendance device pushing data to the API'

    def add_arguments(self, parser):
        parser.add_argument('--device-id', type=int, help='ID of the DeviceConfiguration to use')
        parser.add_argument('--count', type=int, default=10, help='Number of random punches to generate')

    def handle(self, *args, **options):
        device_id = options.get('device_id')
        if device_id:
            try:
                device = DeviceConfiguration.objects.get(id=device_id)
            except DeviceConfiguration.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Device with ID {device_id} not found."))
                return
        else:
            company = Company.objects.first()
            if not company:
                company = Company.objects.create(name="Emulator Company")
            
            device, created = DeviceConfiguration.objects.get_or_create(
                name='Emulator Machine 01',
                company=company,
                defaults={'device_type': 'emulator_v1'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created new device: {device.name}"))

        self.stdout.write(f"Using Device: {device.name} (Token: {device.api_token})")

        employees = list(Employee.objects.filter(company=device.company, is_active=True, deleted_at__isnull=True))
        if not employees:
            self.stdout.write(self.style.WARNING("No active employees found for device's company. Generating random external IDs."))
            employees = [type('Emp', (), {'employee_id': f"EMP-{i:03d}"}) for i in range(1, 6)]

        punches = []
        for _ in range(options['count']):
            emp = random.choice(employees)
            direction = random.choice(['in', 'out'])
            
            now = timezone.now()
            hours_offset = random.randint(-10, 0)
            minutes_offset = random.randint(0, 59)
            punch_time = now + timezone.timedelta(hours=hours_offset, minutes=minutes_offset)

            punches.append({
                "external_id": getattr(emp, 'employee_id', 'UNKNOWN'),
                "punch_time": punch_time.isoformat(),
                "direction": direction,
                "emulator_metadata": "randomly generated"
            })

        self.stdout.write(f"Generated {len(punches)} punches. Sending to API...")

        url = 'http://127.0.0.1:8000/api/v1/device/push/'
        headers = {
            'X-Device-Token': str(device.api_token),
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=punches, headers=headers)
            if response.status_code == 201:
                self.stdout.write(self.style.SUCCESS("Successfully pushed data to API!"))
                self.stdout.write(response.text)
            else:
                self.stderr.write(self.style.ERROR(f"Failed to push. HTTP {response.status_code}"))
                self.stderr.write(response.text)
        except requests.exceptions.ConnectionError:
            self.stderr.write(self.style.ERROR("Connection error. Is the local Django server running on port 8000?"))
