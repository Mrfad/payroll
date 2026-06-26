"""
Base simulator class that all brand simulators inherit from.
Provides HTTP push logic, device registration, and reusable helpers.
"""

import json
import random
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PunchEvent:
    """A single punch event to send to the backend."""

    external_id: str
    punch_time: str  # ISO-8601
    direction: str  # 'in' | 'out'


# Fixed tokens matching the backend's `install` management command.
# Each brand simulator uses a predictable UUID so you can register devices
# once and reuse them across simulator runs.
BRAND_DEFAULT_TOKENS = {
    "hikvision": "00000000-0000-0000-0000-000000000101",
    "zkteco": "00000000-0000-0000-0000-000000000102",
    "anviz": "00000000-0000-0000-0000-000000000103",
    "suprema": "00000000-0000-0000-0000-000000000104",
    "dahua": "00000000-0000-0000-0000-000000000105",
    "idemia": "00000000-0000-0000-0000-000000000106",
    "sifarma": "00000000-0000-0000-0000-000000000107",
}


class BaseDeviceSimulator:
    """
    Base class for attendance machine simulators.

    Subclasses override brand-specific metadata (device_type, serial prefix,
    default config payloads, etc.).
    """

    # --- Override in subclasses ---
    BRAND_NAME = "generic"
    DEVICE_TYPE = "generic_v1"
    SERIAL_PREFIX = "GEN"
    DEFAULT_NAME = "Generic Device"
    DEFAULT_EXTRA_CONFIG = {}
    DEFAULT_AUTH_CREDENTIALS = {}

    def __init__(
        self,
        base_url="http://127.0.0.1:8000",
        api_token=None,
        device_name=None,
        company_id=None,
        auto_register=True,
    ):
        self.base_url = base_url.rstrip("/")
        self.push_url = f"{self.base_url}/api/v1/device/push/"

        # Token resolution priority:
        # 1. Explicit --token flag
        # 2. SIMULATOR_DEVICE_TOKEN env var
        # 3. Fixed per-brand token (matching the register_simulators command)
        # 4. Random UUID as last resort
        self.api_token = api_token
        if not self.api_token:
            self.api_token = self._get_env_token()
        if not self.api_token:
            self.api_token = BRAND_DEFAULT_TOKENS.get(
                self.__class__.__name__.lower()
                .replace("simulator", "")
                .replace("device", ""),
                None,
            )
            # Try the DEVICE_TYPE prefix as a fallback lookup
            if not self.api_token:
                self.api_token = BRAND_DEFAULT_TOKENS.get(
                    self.DEVICE_TYPE.split("_")[0]
                )
        if not self.api_token:
            self.api_token = str(uuid.uuid4())

        self.device_name = device_name or self.DEFAULT_NAME
        self.registered = False

        if auto_register:
            self._register_device_config(company_id)

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------
    def _get_env_token(self):
        import os

        return os.environ.get("SIMULATOR_DEVICE_TOKEN")

    def _register_device_config(self, company_id=None):
        """
        Print instructions for registering the device if it hasn't been
        created in the Django admin yet.
        """
        print(f"[{self.BRAND_NAME}] Device token: {self.api_token}")
        print(
            f"[{self.BRAND_NAME}] Tip: run this once to register the device in your database:"
        )
        print(f"           python manage.py install")
        self.registered = True

    def _try_api_registration(self, company_id=None):
        """Try to create the device via the REST API (may require auth token)."""
        # In a real scenario, you'd need a JWT token for the admin endpoints.
        # For simplicity, we skip this and rely on the user pre-creating a device.
        return False

    # ------------------------------------------------------------------
    # HTTP push
    # ------------------------------------------------------------------
    def push_punch(
        self, external_id: str, punch_time: str, direction: str = "in"
    ) -> bool:
        """
        Send a single punch to the backend.
        Returns True on success.
        """
        payload = json.dumps(
            {
                "external_id": external_id,
                "punch_time": punch_time,
                "direction": direction,
            }
        ).encode("utf-8")

        req = urllib.request.Request(self.push_url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Device-Token", self.api_token)

        try:
            resp = urllib.request.urlopen(req)
            if resp.status == 201:
                body = resp.read().decode()
                result = json.loads(body)
                print(f"  ✓ {external_id} ({direction}) @ {punch_time}")
                return True
            else:
                print(f"  ✗ HTTP {resp.status}: {resp.read().decode()}")
                return False
        except urllib.error.HTTPError as e:
            print(f"  ✗ HTTP {e.code}: {e.read().decode()}")
            return False
        except urllib.error.URLError as e:
            print(f"  ✗ Connection failed — is the server running on {self.base_url}?")
            print(f"    Details: {e}")
            return False

    def push_batch(self, events: list[PunchEvent]) -> tuple[int, int]:
        """
        Send multiple punch events (batched as a list).
        Returns (success_count, fail_count).
        """
        payload = json.dumps(
            [
                {
                    "external_id": e.external_id,
                    "punch_time": e.punch_time,
                    "direction": e.direction,
                }
                for e in events
            ]
        ).encode("utf-8")

        req = urllib.request.Request(self.push_url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Device-Token", self.api_token)

        try:
            resp = urllib.request.urlopen(req)
            if resp.status == 201:
                body = json.loads(resp.read().decode())
                count = body.get("count", len(events))
                print(f"  ✓ Batch of {count} punches sent successfully")
                return count, 0
            else:
                print(f"  ✗ Batch failed: HTTP {resp.status}: {resp.read().decode()}")
                return 0, len(events)
        except urllib.error.HTTPError as e:
            print(f"  ✗ Batch failed: HTTP {e.code}: {e.read().decode()}")
            return 0, len(events)
        except urllib.error.URLError as e:
            print(f"  ✗ Connection failed — is the server running on {self.base_url}?")
            return 0, len(events)

    # ------------------------------------------------------------------
    # Punch generation helpers
    # ------------------------------------------------------------------
    def generate_morning_punch(
        self, employee_id: str, base_date=None, min_hour=7, max_hour=9
    ) -> PunchEvent:
        """Generate a random 'in' punch between min_hour and max_hour."""
        dt = self._random_time(base_date or datetime.now(), min_hour, max_hour)
        return PunchEvent(employee_id, dt.isoformat(), "in")

    def generate_evening_punch(
        self, employee_id: str, base_date=None, min_hour=16, max_hour=18
    ) -> PunchEvent:
        """Generate a random 'out' punch between min_hour and max_hour."""
        dt = self._random_time(base_date or datetime.now(), min_hour, max_hour)
        return PunchEvent(employee_id, dt.isoformat(), "out")

    def _random_time(
        self, base_date: datetime, min_hour: int, max_hour: int
    ) -> datetime:
        """Pick a random time within [min_hour, max_hour) on the given date."""
        hour = random.randint(min_hour, max_hour - 1)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return base_date.replace(hour=hour, minute=minute, second=second, microsecond=0)

    # ------------------------------------------------------------------
    # Device info (brand-specific metadata to log at startup)
    # ------------------------------------------------------------------
    def device_info(self) -> dict:
        return {
            "brand": self.BRAND_NAME,
            "device_type": self.DEVICE_TYPE,
            "name": self.device_name,
            "token": self.api_token,
            "push_url": self.push_url,
        }

    def print_info(self):
        info = self.device_info()
        print(f"\n{'=' * 60}")
        print(f"  {info['brand']} Simulator")
        print(f"  Device type : {info['device_type']}")
        print(f"  Name        : {info['name']}")
        print(f"  Push URL    : {info['push_url']}")
        print(f"  Token       : {info['token']}")
        print(f"{'=' * 60}\n")

    # ------------------------------------------------------------------
    # Interactive / CLI helpers
    # ------------------------------------------------------------------
    def interactive_loop(self, employee_id: str, delay_seconds: float = 3.0):
        """
        Run a simple loop: alternate 'in' / 'out' punches every `delay`.
        Press Ctrl+C to stop.
        """
        print(
            f"\n[{self.BRAND_NAME}] Interactive mode — sending punches every {delay_seconds}s"
        )
        print(f"[{self.BRAND_NAME}] Employee: {employee_id} | Ctrl+C to stop\n")
        direction = "in"
        try:
            while True:
                now = datetime.now()
                self.push_punch(employee_id, now.isoformat(), direction)
                direction = "out" if direction == "in" else "in"
                time.sleep(delay_seconds)
        except KeyboardInterrupt:
            print(f"\n[{self.BRAND_NAME}] Stopped.\n")


# ------------------------------------------------------------------
# Utility: run a simulator from the command line
# ------------------------------------------------------------------
def cli_run(simulator_cls):
    """
    CLI entry point for any brand simulator.

    Usage:
        python -m simulators.hikvision <employee_id> [options]

    Examples:
        python -m simulators.hikvision EMP001
        python -m simulators.hikvision EMP001 --batch
        python -m simulators.hikvision EMP001 --interactive --delay 5
        python -m simulators.hikvision EMP001,EMP002,EMP003 --batch --days 3
    """
    import argparse

    parser = argparse.ArgumentParser(
        description=f"{simulator_cls.BRAND_NAME} Attendance Device Simulator"
    )
    parser.add_argument(
        "employees",
        help="Employee ID(s) to simulate punches for. Comma-separated for multiple.",
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="Backend base URL (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--token", help="Device API token (UUID). If omitted, a new one is generated."
    )
    parser.add_argument(
        "--device-name",
        default=None,
        help=f"Friendly name for the device (default: '{simulator_cls.DEFAULT_NAME}')",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive loop mode (alternates in/out every N seconds)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Seconds between punches in interactive mode (default: 3.0)",
    )
    parser.add_argument(
        "-b",
        "--batch",
        action="store_true",
        help="Generate a batch of historical punch data",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=5,
        help="Number of past days to generate in batch mode (default: 5)",
    )
    parser.add_argument(
        "--direction",
        choices=["in", "out"],
        default="in",
        help="Punch direction for single-punch mode (default: in).",
    )
    parser.add_argument(
        "--company-id",
        help="Company ID to associate the device with (if creating via API)",
    )

    args = parser.parse_args()
    employee_ids = [e.strip() for e in args.employees.split(",")]

    sim = simulator_cls(
        base_url=args.url,
        api_token=args.token,
        device_name=args.device_name,
        company_id=args.company_id,
    )
    sim.print_info()

    if args.interactive:
        sim.interactive_loop(employee_ids[0], delay_seconds=args.delay)
    elif args.batch:
        sim.batch_simulation(employee_ids, days=args.days)
    else:
        # Single immediate punch for each employee
        now = datetime.now()
        for eid in employee_ids:
            sim.push_punch(eid, now.isoformat(), args.direction)
