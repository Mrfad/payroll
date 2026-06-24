import random
from datetime import time, date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from payroll.models import Company, Department, Employee, Shift
from device.models import DeviceConfiguration

class Command(BaseCommand):
    help = 'Generates sample data for testing the payroll and device applications'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting sample data generation...")

        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created (username: admin, password: admin123)'))
        else:
            self.stdout.write(self.style.WARNING('Superuser admin already exists.'))

        # Create Company
        company, created = Company.objects.get_or_create(name='TechNova Solutions')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Company created: {company.name}'))

        # Create Departments
        dept_it, _ = Department.objects.get_or_create(company=company, name='IT Department')
        dept_hr, _ = Department.objects.get_or_create(company=company, name='HR Department')
        dept_ops, _ = Department.objects.get_or_create(company=company, name='Operations')

        # Create Shift
        shift, _ = Shift.objects.get_or_create(
            company=company,
            name='Standard Day Shift',
            defaults={'start_time': time(9, 0), 'end_time': time(17, 0)}
        )

        # Create Users and Employees
        employees_data = [
            {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'emp_id': 'EMP001', 'dept': dept_it, 'designation': 'Software Engineer'},
            {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'emp_id': 'EMP002', 'dept': dept_hr, 'designation': 'HR Manager'},
            {'username': 'alice_jones', 'first_name': 'Alice', 'last_name': 'Jones', 'emp_id': 'EMP003', 'dept': dept_ops, 'designation': 'Operations Lead'},
        ]

        for data in employees_data:
            user, u_created = User.objects.get_or_create(username=data['username'])
            if u_created:
                user.set_password('pass1234')
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                user.save()

            emp, e_created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'company': company,
                    'department': data['dept'],
                    'employee_id': data['emp_id'],
                    'designation': data['designation'],
                    'base_salary': 5000.00,
                    'device_user_ids': {'zkteco': data['emp_id'].replace('EMP', ''), 'hikvision': data['emp_id'], 'dahua': data['emp_id']}
                }
            )
            if e_created:
                self.stdout.write(self.style.SUCCESS(f"Employee created: {emp.employee_id} - {user.get_full_name()}"))

        # Create Device Configurations for major biometric companies
        devices = [
            {
                'name': 'Main Entrance - ZKTeco K40',
                'device_type': 'zkteco_k40',
                'ip_address': '192.168.1.201',
                'port': 4370,
                'api_endpoint': None,
                'auth_credentials': {},
                'extra_config': {'protocol': 'UDP'}
            },
            {
                'name': 'Office Door - Hikvision ISAPI Face Recognition',
                'device_type': 'hikvision_isapi',
                'ip_address': '192.168.1.202',
                'port': 80,
                'api_endpoint': 'http://192.168.1.202/ISAPI/AccessControl/AcsEvent',
                'auth_credentials': {'username': 'admin', 'password': 'password123'},
                'extra_config': {'digest_auth': True}
            },
            {
                'name': 'Back Door - Dahua Access Control',
                'device_type': 'dahua',
                'ip_address': '192.168.1.203',
                'port': 37777,
                'api_endpoint': None,
                'auth_credentials': {'username': 'admin', 'password': 'admin'},
                'extra_config': {}
            },
            {
                'name': 'Server Room - Suprema BioStar 2',
                'device_type': 'suprema_biostar_v2',
                'ip_address': '192.168.1.204',
                'port': 443,
                'api_endpoint': 'https://192.168.1.204/api/v2',
                'auth_credentials': {'api_key': 'suprema_secret_key_999'},
                'extra_config': {'verify_ssl': False}
            }
        ]

        for d_data in devices:
            device, d_created = DeviceConfiguration.objects.get_or_create(
                name=d_data['name'],
                company=company,
                defaults={
                    'device_type': d_data['device_type'],
                    'ip_address': d_data['ip_address'],
                    'port': d_data['port'],
                    'api_endpoint': d_data['api_endpoint'],
                    'auth_credentials': d_data['auth_credentials'],
                    'extra_config': d_data['extra_config']
                }
            )
            if d_created:
                self.stdout.write(self.style.SUCCESS(f"Device created: {device.name}"))

        self.stdout.write(self.style.SUCCESS("Sample data generation completed successfully! You can login with admin / admin123"))
