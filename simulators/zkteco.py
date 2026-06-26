"""
ZKTeco Attendance Device Simulator
===================================
Simulates ZKTeco biometric devices (formerly ZKSoftware/ZKTechnology).

Popular models: K30, MB360, inBio460, SpeedFace V5L.

ZKTeco devices typically use the ZK protocol (UDP/TCP) for real-time
communication, but their 'Push SDK' or 'ZKBioSecurity' middleware can
forward attendance transactions via HTTP to a remote server.

Device types commonly seen: 'zkteco_k30', 'zkteco_mb360', 'zkteco_speedface'
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from base import BaseDeviceSimulator, PunchEvent, cli_run


class ZKTecoSimulator(BaseDeviceSimulator):
    BRAND_NAME = "ZKTeco"
    DEVICE_TYPE = "zkteco_k30"
    SERIAL_PREFIX = "ZK"
    DEFAULT_NAME = "Factory Floor Biometric Reader"
    DEFAULT_EXTRA_CONFIG = {
        "firmware_version": "ZKBio 8.0.23",
        "protocol": "ZK-ICP",
        "fingerprint_capacity": 4000,
        "face_capacity": 1000,
        "card_capacity": 10000,
        "palm_capacity": 500,
        "recognition_mode": "fingerprint+face",
        "verification_speed": "0.3s",
        "push_interval_seconds": 30,
        "network_settings": {
            "dhcp": True,
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.0.1",
        },
    }
    DEFAULT_AUTH_CREDENTIALS = {"username": "admin", "password": "zkteco123"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_number = (
            f"ZK{datetime.now().strftime('%Y%m%d')}{random.randint(10000, 99999)}"
        )
        self.mac_address = (
            f"00:17:61:{':'.join(f'{random.randint(0, 255):02X}' for _ in range(3))}"
        )

    def device_info(self) -> dict:
        info = super().device_info()
        info["serial_number"] = self.serial_number
        info["mac_address"] = self.mac_address
        info["ip_address"] = f"192.168.0.{random.randint(100, 250)}"
        info["port"] = 4370  # ZK standard TCP port
        info["extra_config"] = self.DEFAULT_EXTRA_CONFIG
        return info

    def batch_simulation(self, employee_ids: list[str], days: int = 5):
        """
        Simulate ZKTeco device pushing attendance with realistic patterns:
        - Standard shift (8:00-17:00)
        - Some employees arrive late or leave early (random)
        - Occasional overtime punch
        """
        print(
            f"\n[{self.BRAND_NAME}] Generating {days} days of ZKTeco attendance data...\n"
        )

        total = 0
        for day_offset in range(days, 0, -1):
            base_date = datetime.now() - timedelta(days=day_offset)
            if base_date.weekday() >= 5:
                continue  # skip weekends

            events = []
            for eid in employee_ids:
                # Most employees arrive between 7:30 - 8:30
                morning_hour = 7 if random.random() < 0.3 else 8
                events.append(
                    self.generate_morning_punch(
                        eid, base_date, morning_hour, morning_hour + 1
                    )
                )

                # Most leave between 17:00 - 18:00
                evening_hour = 17 if random.random() < 0.7 else 18
                events.append(
                    self.generate_evening_punch(
                        eid, base_date, evening_hour, evening_hour + 1
                    )
                )

                # ~15% chance of overtime punch (an extra 'in' after 19:00)
                if random.random() < 0.15:
                    ot_hour = random.randint(19, 21)
                    events.append(
                        self.generate_morning_punch(
                            eid, base_date, ot_hour, ot_hour + 1
                        )
                    )
                    # and an 'out' 2-3 hours later
                    ot_out = base_date.replace(
                        hour=ot_hour + 2, minute=random.randint(0, 59)
                    )
                    events.append(PunchEvent(eid, ot_out.isoformat(), "out"))

            ok, fail = self.push_batch(events)
            total += ok

        print(
            f"\n[{self.BRAND_NAME}] Done — {total} punches sent across {days} day(s)\n"
        )


if __name__ == "__main__":
    cli_run(ZKTecoSimulator)
