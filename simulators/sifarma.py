"""
Sifarma Attendance Device Simulator
====================================
Simulates Sifarma biometric devices (popular in Latin America & Southern Europe).

Sifarma devices are known for reliable fingerprint and proximity card readers
used in workforce management. They often use proprietary UDP/TCP protocols
with an HTTP bridge for cloud push.

Device types commonly seen: 'sifarma_biometric', 'sifarma_fp2000'
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from base import BaseDeviceSimulator, PunchEvent, cli_run


class SifarmaSimulator(BaseDeviceSimulator):
    BRAND_NAME = "Sifarma"
    DEVICE_TYPE = "sifarma_biometric"
    SERIAL_PREFIX = "SF"
    DEFAULT_NAME = "Sifarma Biometric Reader"
    DEFAULT_EXTRA_CONFIG = {
        "firmware_version": "SifarmaOS 3.1.2",
        "protocol": "SifarmaTCP",
        "fingerprint_capacity": 5000,
        "card_capacity": 10000,
        "recognition_mode": "fingerprint+card",
        "communication": {
            "default_port": 3000,
            "protocol_type": "TCP/IP",
            "encryption": "AES-128",
            "push_enabled": True,
            "push_interval_seconds": 60,
        },
        "display": {
            "language": "pt-BR",
            "time_format": "24h",
            "date_format": "DD/MM/YYYY",
        },
    }
    DEFAULT_AUTH_CREDENTIALS = {"username": "admin", "password": "sifarma@123"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_number = (
            f"SF{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        )
        self.mac_address = (
            f"00:1B:1A:{':'.join(f'{random.randint(0, 255):02X}' for _ in range(3))}"
        )

    def device_info(self) -> dict:
        info = super().device_info()
        info["serial_number"] = self.serial_number
        info["mac_address"] = self.mac_address
        info["ip_address"] = f"192.168.0.{random.randint(10, 250)}"
        info["port"] = 3000
        info["extra_config"] = self.DEFAULT_EXTRA_CONFIG
        return info

    def batch_simulation(self, employee_ids: list[str], days: int = 5):
        """
        Simulate Sifarma device with Brazilian work patterns:
        - 44-hour work week (Mon-Sat with half-day Saturday)
        - 1-hour lunch break
        """
        print(
            f"\n[{self.BRAND_NAME}] Generating {days} days of Sifarma data (Brazilian schedule)...\n"
        )

        total = 0
        for day_offset in range(days, 0, -1):
            base_date = datetime.now() - timedelta(days=day_offset)
            is_saturday = base_date.weekday() == 5
            if base_date.weekday() >= 6:
                continue  # skip Sunday

            events = []
            for eid in employee_ids:
                if is_saturday:
                    # Saturday: 8:00 - 12:00 (half day)
                    events.append(self.generate_morning_punch(eid, base_date, 8, 9))
                    events.append(self.generate_evening_punch(eid, base_date, 11, 12))
                else:
                    # Weekday: 8:00 in, 12:00 lunch out, 13:00 lunch in, 18:00 out
                    events.append(self.generate_morning_punch(eid, base_date, 8, 8))
                    lunch_out_time = base_date.replace(
                        hour=12, minute=random.randint(0, 5)
                    )
                    events.append(PunchEvent(eid, lunch_out_time.isoformat(), "out"))
                    lunch_in_time = base_date.replace(
                        hour=13, minute=random.randint(0, 5)
                    )
                    events.append(PunchEvent(eid, lunch_in_time.isoformat(), "in"))
                    events.append(self.generate_evening_punch(eid, base_date, 17, 18))

            ok, fail = self.push_batch(events)
            total += ok

        print(
            f"\n[{self.BRAND_NAME}] Done — {total} punches across {days} day(s) (Mon-Sat schedule)\n"
        )


if __name__ == "__main__":
    cli_run(SifarmaSimulator)
