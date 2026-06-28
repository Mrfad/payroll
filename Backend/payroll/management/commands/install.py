# Backend\payroll\management\commands\install.py
from companies.models import Company, Department

"""
Management command to set up the ultimate demo environment.
Creates an admin user, a company, registers all 7 simulator devices,
and optionally creates dummy employees.

Usage:
    python manage.py install
    python manage.py install --with-employees
    python manage.py install --no-input
"""
import sys

from device.models import DeviceConfiguration
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from payroll.models import Company, Department, Employee

# Fixed, recognizable UUIDs for each simulator brand.
SIMULATOR_TOKENS = {
    "hikvision": "00000000-0000-0000-0000-000000000101",
    "zkteco": "00000000-0000-0000-0000-000000000102",
    "anviz": "00000000-0000-0000-0000-000000000103",
    "suprema": "00000000-0000-0000-0000-000000000104",
    "dahua": "00000000-0000-0000-0000-000000000105",
    "idemia": "00000000-0000-0000-0000-000000000106",
    "sifarma": "00000000-0000-0000-0000-000000000107",
}

SIMULATOR_META = {
    "hikvision": {
        "name": "Hikvision DS-K1T6 (Sim)",
        "device_type": "hikvision_ds-k1t6",
        "ip_address": "192.168.1.100",
        "port": 80,
        "serial_number": "DS-K1T62024010001",
        "extra_config": {"firmware_version": "V2.3.8_build202403", "protocol": "ISAPI"},
        "auth_credentials": {"username": "admin", "digest_auth": True},
    },
    "zkteco": {
        "name": "ZKTeco K30 (Sim)",
        "device_type": "zkteco_k30",
        "ip_address": "192.168.0.100",
        "port": 4370,
        "serial_number": "ZK2024010110001",
        "extra_config": {"firmware_version": "ZKBio 8.0.23", "protocol": "ZK-ICP"},
        "auth_credentials": {"username": "admin"},
    },
    "anviz": {
        "name": "Anviz VF30 (Sim)",
        "device_type": "anviz_vf30",
        "ip_address": "10.0.0.100",
        "port": 5010,
        "serial_number": "ANV012410001",
        "extra_config": {
            "firmware_version": "CrossChex 4.12.5",
            "protocol": "AnvizTCP",
        },
        "auth_credentials": {"username": "admin"},
    },
    "suprema": {
        "name": "Suprema BioStation 2 (Sim)",
        "device_type": "suprema_biostation2",
        "ip_address": "172.16.0.100",
        "port": 8443,
        "serial_number": "SUP202401010001",
        "extra_config": {"firmware_version": "BIO_STATION_2_1.8.2"},
        "auth_credentials": {"username": "superadmin"},
    },
    "dahua": {
        "name": "Dahua AS7212X (Sim)",
        "device_type": "dahua_as7212x",
        "ip_address": "192.168.2.100",
        "port": 80,
        "serial_number": "DH202401000001",
        "extra_config": {
            "firmware_version": "DH_IPS_V4.2.8_202403",
            "protocol": "DahuaHTTP",
        },
        "auth_credentials": {"username": "admin"},
    },
    "idemia": {
        "name": "IDEMIA MorphoWave (Sim)",
        "device_type": "idemia_morphowave",
        "ip_address": "10.10.1.100",
        "port": 443,
        "serial_number": "MW20240100001",
        "extra_config": {"firmware_version": "MorphoWave_Compact_2.6.4"},
        "auth_credentials": {"username": "security_admin"},
    },
    "sifarma": {
        "name": "Sifarma Biometric (Sim)",
        "device_type": "sifarma_biometric",
        "ip_address": "192.168.0.101",
        "port": 3000,
        "serial_number": "SF202401011001",
        "extra_config": {
            "firmware_version": "SifarmaOS 3.1.2",
            "protocol": "SifarmaTCP",
        },
        "auth_credentials": {"username": "admin"},
    },
}


class Command(BaseCommand):
    help = "The Ultimate Installation Command. Creates company, admin, 7 devices, and optionally dummy users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Skip interactive prompts (will not create dummy employees unless specified).",
        )
        parser.add_argument(
            "--with-employees",
            action="store_true",
            help="Create dummy employees automatically without prompting.",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🚀 Starting the Ultimate Environment Setup...\n")
        )

        # 1. Create superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Superuser created (username: admin, password: admin123)"
                )
            )
        else:
            self.stdout.write("✓ Superuser admin already exists.")

        # 2. Create Company
        company, created = Company.objects.get_or_create(name="TechNova Solutions")
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Company created: {company.name}"))
        else:
            self.stdout.write(f"✓ Company {company.name} already exists.")

        # 3. Create 7 Simulator Devices
        self.stdout.write("\n🔌 Setting up Simulator Devices...")
        for brand, token in SIMULATOR_TOKENS.items():
            meta = SIMULATOR_META[brand]
            device, created = DeviceConfiguration.objects.get_or_create(
                api_token=token,
                defaults={
                    "company": company,
                    "name": meta["name"],
                    "device_type": meta["device_type"],
                    "ip_address": meta["ip_address"],
                    "port": meta["port"],
                    "serial_number": meta["serial_number"],
                    "extra_config": meta["extra_config"],
                    "auth_credentials": meta["auth_credentials"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {meta['name']}"))
            else:
                self.stdout.write(f"  · Exists : {meta['name']}")

        # 4. Dummy Users Prompt
        create_emps = options["with_employees"]
        if not create_emps and not options["no_input"]:
            # Ask interactively
            answer = input(
                "\n👨‍💼 Do you want to create 5 dummy employees for testing? (y/N): "
            )
            if answer.lower() in ["y", "yes"]:
                create_emps = True

        if create_emps:
            self.stdout.write("\n👨‍💼 Creating dummy employees...")
            department, _ = Department.objects.get_or_create(
                company=company, name="General"
            )

            created_count = 0
            for i in range(1, 6):
                emp_id = f"EMP{i:03d}"
                username = f"employee_{emp_id.lower()}"

                if Employee.objects.filter(employee_id=emp_id).exists():
                    self.stdout.write(f"  · {emp_id} already exists")
                    continue

                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": "Test",
                        "last_name": f"Employee {i}",
                        "email": f"{username}@example.com",
                    },
                )
                user.set_password("test1234")
                user.save()

                Employee.objects.create(
                    user=user,
                    company=company,
                    department=department,
                    employee_id=emp_id,
                    is_active=True,
                )
                self.stdout.write(self.style.SUCCESS(f"  ✓ {emp_id} created"))
                created_count += 1

            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nCreated {created_count} dummy employees. Password is 'test1234' for all."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("\n✅ Setup Complete! You are ready to go!")
        )
