"""
Suprema Attendance Device Simulator
====================================
Simulates Suprema biometric devices (e.g., BioStation 2, FaceStation 2, XPass).

Suprema is a South Korean biometric company known for high-security solutions
used in enterprise and government sectors. Devices use the Suprema SDK/API
and can push events to a remote server via HTTP.

Device types commonly seen: 'suprema_biostation2', 'suprema_facestation2',
'suprema_xpass'
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from base import BaseDeviceSimulator, PunchEvent, cli_run


class SupremaSimulator(BaseDeviceSimulator):
    BRAND_NAME = "Suprema"
    DEVICE_TYPE = "suprema_biostation2"
    SERIAL_PREFIX = "SB2"
    DEFAULT_NAME = "HQ Secure Entrance BioStation 2"
    DEFAULT_EXTRA_CONFIG = {
        "firmware_version": "BIO_STATION_2_1.8.2",
        "sdk_version": "Suprema SDK 2.0",
        "fingerprint_capacity": 500000,
        "face_capacity": 30000,
        "card_capacity": 500000,
        "recognition_mode": "fingerprint+face+card",
        "security_level": "high",
        "liveness_detection": True,
        "anti_passback": True,
        "communication": {
            "protocol": "HTTPS",
            "api_port": 443,
            "device_discovery": "SSDP",
            "backup_server": {"enabled": True, "ip": "192.168.1.10", "port": 8443},
        },
        "access_levels": ["employee", "manager", "admin", "security"],
        "time_attendance": {
            "auto_sync": True,
            "sync_interval_minutes": 5,
            "overtime_tracking": True,
            "break_tracking": True,
        },
    }
    DEFAULT_AUTH_CREDENTIALS = {
        "username": "superadmin",
        "password": "Suprema@2024!",
        "api_key": "sk_live_" + "".join(random.choices("abcdef0123456789", k=32)),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_number = (
            f"SUP{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        )
        self.mac_address = (
            f"00:16:6C:{':'.join(f'{random.randint(0, 255):02X}' for _ in range(3))}"
        )

    def device_info(self) -> dict:
        info = super().device_info()
        info["serial_number"] = self.serial_number
        info["mac_address"] = self.mac_address
        info["ip_address"] = f"172.16.0.{random.randint(10, 200)}"
        info["port"] = 8443
        info["extra_config"] = self.DEFAULT_EXTRA_CONFIG
        return info

    def batch_simulation(self, employee_ids: list[str], days: int = 5):
        """
        Simulate Suprema device with strict access-control + attendance.
        Includes multiple punch types and door access events.
        """
        print(
            f"\n[{self.BRAND_NAME}] Generating {days} days of Suprema data (with access events)...\n"
        )

        total = 0
        for day_offset in range(days, 0, -1):
            base_date = datetime.now() - timedelta(days=day_offset)
            if base_date.weekday() >= 5:
                continue

            events = []
            for eid in employee_ids:
                # Suprema devices often log multiple events per day:
                # 1. Morning entry    (07:30 - 08:30)
                events.append(self.generate_morning_punch(eid, base_date, 7, 8))
                # 2. Lunch break out  (12:00 - 12:30) — ~40% of employees go out for lunch
                if random.random() < 0.4:
                    lunch_out = base_date.replace(hour=12, minute=random.randint(0, 30))
                    events.append(PunchEvent(eid, lunch_out.isoformat(), "out"))
                    # Lunch back in (12:45 - 13:30)
                    lunch_in = base_date.replace(hour=12, minute=random.randint(45, 59))
                    if random.random() < 0.5:
                        lunch_in = base_date.replace(
                            hour=13, minute=random.randint(0, 30)
                        )
                    events.append(PunchEvent(eid, lunch_in.isoformat(), "in"))
                # 3. Evening exit     (17:00 - 18:30)
                events.append(self.generate_evening_punch(eid, base_date, 17, 18))

            ok, fail = self.push_batch(events)
            total += ok

        print(
            f"\n[{self.BRAND_NAME}] Done — {total} events sent (including lunch breaks & door access)\n"
        )


if __name__ == "__main__":
    cli_run(SupremaSimulator)
