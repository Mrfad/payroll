"""
Anviz Attendance Device Simulator
==================================
Simulates Anviz biometric devices (e.g., Anviz VF30, Anviz T5, CrossChex).

Anviz devices are popular in access control and time attendance. They use
different protocol generations: Wiegand, Anviz Protocol (serial/TCP), and
modern CrossChex Cloud push.

Device types commonly seen: 'anviz_vf30', 'anviz_crosschex', 'anviz_t5'
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from base import BaseDeviceSimulator, PunchEvent, cli_run


class AnvizSimulator(BaseDeviceSimulator):
    BRAND_NAME = "Anviz"
    DEVICE_TYPE = "anviz_vf30"
    SERIAL_PREFIX = "AV"
    DEFAULT_NAME = "Side Door Anviz Reader"
    DEFAULT_EXTRA_CONFIG = {
        "firmware_version": "CrossChex 4.12.5",
        "protocol": "AnvizTCP",
        "fingerprint_capacity": 3000,
        "face_capacity": 500,
        "card_capacity": 8000,
        "recognition_mode": "fingerprint+card",
        "communication": {
            "protocol_type": "TCP/IP",
            "default_port": 5010,
            "encryption": "AES-128",
            "heartbeat_interval_seconds": 10,
        },
        "relay_config": {
            "door_1": "Main Entrance",
            "door_2": "Side Door",
            "door_lock_seconds": 5,
        },
    }
    DEFAULT_AUTH_CREDENTIALS = {"username": "admin", "password": "anviz2024!"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_number = (
            f"ANV{datetime.now().strftime('%m%d')}{random.randint(10000, 99999)}"
        )
        self.mac_address = (
            f"00:0C:76:{':'.join(f'{random.randint(0, 255):02X}' for _ in range(3))}"
        )

    def device_info(self) -> dict:
        info = super().device_info()
        info["serial_number"] = self.serial_number
        info["mac_address"] = self.mac_address
        info["ip_address"] = f"10.0.0.{random.randint(10, 200)}"
        info["port"] = 5010
        info["extra_config"] = self.DEFAULT_EXTRA_CONFIG
        return info

    def batch_simulation(self, employee_ids: list[str], days: int = 5):
        """
        Simulate Anviz device with shift-based attendance.
        Generates punches for three common shift patterns:
        - Morning shift: 6:00 in, 14:00 out
        - Day shift:    8:00 in, 17:00 out
        - Night shift:  20:00 in, 5:00 out (next day)
        """
        print(f"\n[{self.BRAND_NAME}] Generating {days} days of Anviz shift data...\n")

        shifts = [
            {"name": "Morning", "in_hour": 6, "out_hour": 14},
            {"name": "Day", "in_hour": 8, "out_hour": 17},
            {"name": "Night", "in_hour": 20, "out_hour": 5},
        ]

        total = 0
        for day_offset in range(days, 0, -1):
            base_date = datetime.now() - timedelta(days=day_offset)
            if base_date.weekday() >= 5:
                continue

            events = []
            for i, eid in enumerate(employee_ids):
                # Distribute employees across shifts
                shift = shifts[i % len(shifts)]
                punch_date = base_date

                # Morning 'in'
                in_time = punch_date.replace(
                    hour=shift["in_hour"], minute=random.randint(0, 59)
                )
                events.append(PunchEvent(eid, in_time.isoformat(), "in"))

                # Evening/night 'out'
                out_hour = shift["out_hour"]
                if out_hour < 12:
                    # Night shift goes past midnight
                    out_time = (punch_date + timedelta(days=1)).replace(
                        hour=out_hour, minute=random.randint(0, 59)
                    )
                else:
                    out_time = punch_date.replace(
                        hour=out_hour, minute=random.randint(0, 59)
                    )
                events.append(PunchEvent(eid, out_time.isoformat(), "out"))

            ok, fail = self.push_batch(events)
            total += ok

        print(
            f"\n[{self.BRAND_NAME}] Done — {total} punches across {days} day(s) with {len(shifts)} shift patterns\n"
        )


if __name__ == "__main__":
    cli_run(AnvizSimulator)
