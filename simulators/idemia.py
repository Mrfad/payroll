"""
IDEMIA (Morpho) Attendance Device Simulator
============================================
Simulates IDEMIA/Morpho biometric devices (e.g., MorphoWave, Sigma, VisionAccess).

IDEMIA is a French multinational providing high-security biometric solutions for
government, banking, and large enterprises. Their devices use the MorphoWave
technology (contactless fingerprint) and the BioAPI / MorphoAPI protocol.

Device types commonly seen: 'idemia_morphowave', 'idemia_sigma', 'idemia_visionaccess'
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from base import BaseDeviceSimulator, PunchEvent, cli_run


class IDEMIASimulator(BaseDeviceSimulator):
    BRAND_NAME = "IDEMIA"
    DEVICE_TYPE = "idemia_morphowave"
    SERIAL_PREFIX = "MW"
    DEFAULT_NAME = "HQ Secure Entrance MorphoWave"
    DEFAULT_EXTRA_CONFIG = {
        "firmware_version": "MorphoWave_Compact_2.6.4",
        "sdk_version": "MorphoAPI 3.2.1",
        "fingerprint_capacity": 100000,
        "face_capacity": 50000,
        "iris_capacity": 20000,
        "recognition_mode": "contactless_fingerprint+face+iris",
        "security_level": "very_high",
        "liveness_detection": True,
        "anti_spoofing": True,
        "match_speed": "< 0.3s (1:N, 100K users)",
        "communication": {
            "protocol": "HTTPS/REST",
            "api_port": 443,
            "certificate_based_auth": True,
            "ldap_integration": True,
            "redundancy": {"mode": "active-active", "sync_protocol": "MorphoCluster"},
        },
        "compliance": {
            "fips_201": True,
            "iso_27001": True,
            "gdpr_compliant": True,
            "audit_trail": True,
        },
        "additional_sensors": {
            "temperature": True,
            "mask_detection": True,
            "tamper_detection": True,
        },
    }
    DEFAULT_AUTH_CREDENTIALS = {
        "username": "security_admin",
        "password": "M0rph0$ecure!",
        "client_cert": "sha256:f3a1b2c3... (mocked)",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_number = (
            f"MW{datetime.now().strftime('%Y%m')}{random.randint(10000, 99999)}"
        )
        self.mac_address = (
            f"00:50:C2:{':'.join(f'{random.randint(0, 255):02X}' for _ in range(3))}"
        )

    def device_info(self) -> dict:
        info = super().device_info()
        info["serial_number"] = self.serial_number
        info["mac_address"] = self.mac_address
        info["ip_address"] = f"10.10.{random.randint(1, 10)}.{random.randint(10, 250)}"
        info["port"] = 443
        info["extra_config"] = self.DEFAULT_EXTRA_CONFIG
        return info

    def batch_simulation(self, employee_ids: list[str], days: int = 5):
        """
        Simulate IDEMIA device with enterprise-grade attendance.
        Includes 24-hour, multi-site, and shift rotation patterns.
        """
        print(
            f"\n[{self.BRAND_NAME}] Generating {days} days of IDEMIA enterprise data...\n"
        )

        shifts = [
            ("early", 6, 14),
            ("morning", 8, 16),
            ("late", 10, 18),
            ("night_a", 22, 6),  # overnight
            ("night_b", 0, 8),  # overnight
        ]

        total = 0
        for day_offset in range(days, 0, -1):
            base_date = datetime.now() - timedelta(days=day_offset)
            # IDEMIA devices don't skip weekends (some sites are 24/7)
            if base_date.weekday() >= 5:
                # Weekend — only ~30% of employees work
                weekend_workers = [eid for eid in employee_ids if random.random() < 0.3]
                if not weekend_workers:
                    continue
                emp_pool = weekend_workers
            else:
                emp_pool = employee_ids

            events = []
            for i, eid in enumerate(emp_pool):
                shift_name, in_hour, out_hour = shifts[i % len(shifts)]

                if out_hour < in_hour:
                    # Overnight shift
                    in_time = base_date.replace(
                        hour=in_hour, minute=random.randint(0, 59)
                    )
                    out_date = base_date + timedelta(days=1)
                    out_time = out_date.replace(
                        hour=out_hour, minute=random.randint(0, 59)
                    )
                    events.append(PunchEvent(eid, in_time.isoformat(), "in"))
                    events.append(PunchEvent(eid, out_time.isoformat(), "out"))
                else:
                    events.append(
                        self.generate_morning_punch(
                            eid, base_date, in_hour, in_hour + 1
                        )
                    )
                    events.append(
                        self.generate_evening_punch(
                            eid, base_date, out_hour, out_hour + 1
                        )
                    )

                # ~5% of senior staff get an additional out-in (meeting outside)
                if random.random() < 0.05:
                    meeting_out = base_date.replace(
                        hour=10, minute=random.randint(0, 30)
                    )
                    meeting_in = base_date.replace(
                        hour=11, minute=random.randint(0, 30)
                    )
                    events.append(PunchEvent(eid, meeting_out.isoformat(), "out"))
                    events.append(PunchEvent(eid, meeting_in.isoformat(), "in"))

            ok, fail = self.push_batch(events)
            total += ok

        print(
            f"\n[{self.BRAND_NAME}] Done — {total} enterprise events across {days} day(s)\n"
        )


if __name__ == "__main__":
    cli_run(IDEMIASimulator)
