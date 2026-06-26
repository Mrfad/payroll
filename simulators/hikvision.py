"""
Hikvision Attendance Device Simulator
======================================
Simulates Hikvision face recognition terminals (e.g., DS-K1T6 series).

Real Hikvision devices use ISAPI protocol internally, but when configured
to push to a remote server they send XML/JSON payloads via HTTP POST.

Device types commonly seen: 'hikvision_ds-k1t6', 'hikvision_face_terminal'
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

from base import BaseDeviceSimulator, PunchEvent, cli_run


class HikvisionSimulator(BaseDeviceSimulator):
    BRAND_NAME = "Hikvision"
    DEVICE_TYPE = "hikvision_ds-k1t6"
    SERIAL_PREFIX = "DS-K1T6"
    DEFAULT_NAME = "Main Entrance Face Terminal"
    DEFAULT_EXTRA_CONFIG = {
        "firmware_version": "V2.3.8_build202403",
        "protocol": "ISAPI",
        "face_capacity": 3000,
        "fingerprint_capacity": 5000,
        "card_capacity": 10000,
        "recognition_mode": "face+card",
        "liveness_detection": True,
        "network_settings": {
            "dhcp": False,
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "dns": "8.8.8.8",
        },
    }
    DEFAULT_AUTH_CREDENTIALS = {
        "username": "admin",
        "password": "hikvision123!",
        "digest_auth": True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hikvision devices often have a serial number based on MAC
        mac_prefix = "4C:65:A8"
        mac_suffix = ":".join(f"{random.randint(0, 255):02X}" for _ in range(3))
        self.serial_number = f"{self.SERIAL_PREFIX}{datetime.now().strftime('%Y%m')}{random.randint(100000, 999999)}"
        self.mac_address = f"{mac_prefix}:{mac_suffix}"

    def device_info(self) -> dict:
        info = super().device_info()
        info["serial_number"] = self.serial_number
        info["mac_address"] = self.mac_address
        info["ip_address"] = f"192.168.1.{random.randint(50, 200)}"
        info["extra_config"] = self.DEFAULT_EXTRA_CONFIG
        return info

    def batch_simulation(self, employee_ids: list[str], days: int = 5):
        """
        Simulate a full work-week of attendance data as if pushed from
        a Hikvision face terminal.
        """
        print(f"\n[{self.BRAND_NAME}] Generating {days} days of attendance data...\n")

        total = 0
        for day_offset in range(days, 0, -1):
            base_date = datetime.now() - timedelta(days=day_offset)
            # Skip weekends
            if base_date.weekday() >= 5:
                continue

            events = []
            for eid in employee_ids:
                # Morning check-in (7:00 - 9:00)
                events.append(self.generate_morning_punch(eid, base_date, 7, 9))
                # Afternoon check-out (16:00 - 18:00)
                events.append(self.generate_evening_punch(eid, base_date, 16, 18))

            ok, fail = self.push_batch(events)
            total += ok

        print(
            f"\n[{self.BRAND_NAME}] Done — {total} punches sent across {days} day(s)\n"
        )


if __name__ == "__main__":
    cli_run(HikvisionSimulator)
