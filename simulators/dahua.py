"""
Dahua Attendance Device Simulator
==================================
Simulates Dahua face recognition terminals (e.g., Dahua DHI-AS7212x, DH-IPM).

Dahua is a major Chinese video surveillance & access control manufacturer.
Their face recognition terminals use HTTP push to notify attendance events.

Device types commonly seen: 'dahua_as7212x', 'dahua_face_terminal', 'dahua_vto'
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from base import BaseDeviceSimulator, PunchEvent, cli_run


class DahuaSimulator(BaseDeviceSimulator):
    BRAND_NAME = "Dahua"
    DEVICE_TYPE = "dahua_as7212x"
    SERIAL_PREFIX = "DH"
    DEFAULT_NAME = "Warehouse Face Recognition Terminal"
    DEFAULT_EXTRA_CONFIG = {
        "firmware_version": "DH_IPS_V4.2.8_202403",
        "protocol": "DahuaHTTP",
        "face_capacity": 5000,
        "fingerprint_capacity": 5000,
        "card_capacity": 10000,
        "recognition_mode": "face+capture",
        "capture": {
            "resolution": "1920x1080",
            "snap_on_pass": True,
            "snap_on_deny": True,
            "face_quality": "high",
        },
        "communication": {
            "push_protocol": "HTTP POST",
            "data_format": "JSON",
            "alarm_events": True,
            "temperature_detection": True,
            "mask_detection": True,
        },
        "display": {
            "screen_size": "8 inch",
            "brightness": 80,
            "language": "en",
            "welcome_message": "Welcome to Dahua",
        },
    }
    DEFAULT_AUTH_CREDENTIALS = {
        "username": "admin",
        "password": "dahua2024!",
        "realm": "Dahua HTTP Server",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_number = (
            f"DH{datetime.now().strftime('%Y%m')}{random.randint(100000, 999999)}"
        )
        self.mac_address = (
            f"E0:9D:3A:{':'.join(f'{random.randint(0, 255):02X}' for _ in range(3))}"
        )

    def device_info(self) -> dict:
        info = super().device_info()
        info["serial_number"] = self.serial_number
        info["mac_address"] = self.mac_address
        info["ip_address"] = f"192.168.2.{random.randint(10, 250)}"
        info["port"] = 80
        info["extra_config"] = self.DEFAULT_EXTRA_CONFIG
        return info

    def batch_simulation(self, employee_ids: list[str], days: int = 5):
        """
        Simulate Dahua device with temperature and mask events alongside attendance.
        """
        print(
            f"\n[{self.BRAND_NAME}] Generating {days} days of Dahua data (with temp/mask events)...\n"
        )

        total = 0
        for day_offset in range(days, 0, -1):
            base_date = datetime.now() - timedelta(days=day_offset)
            if base_date.weekday() >= 5:
                continue

            events = []
            for eid in employee_ids:
                # Morning check-in with wider window (06:30 - 09:30) for factory workers
                events.append(self.generate_morning_punch(eid, base_date, 6, 9))
                # ~30% present in afternoon but skip lunch out (Dahua often does single direction)
                events.append(self.generate_evening_punch(eid, base_date, 16, 19))

                # ~10% have a second entry/exit for split shifts
                if random.random() < 0.1:
                    events.append(self.generate_morning_punch(eid, base_date, 12, 13))
                    events.append(self.generate_evening_punch(eid, base_date, 20, 22))

            ok, fail = self.push_batch(events)
            total += ok

        print(f"\n[{self.BRAND_NAME}] Done — {total} punches across {days} day(s)\n")


if __name__ == "__main__":
    cli_run(DahuaSimulator)
