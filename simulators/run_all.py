"""
Run multiple device simulators at once to generate a realistic test dataset.

Usage:
    python -m simulators.run_all <employee_id1,employee_id2,...> [options]

Examples:
    python -m simulators.run_all EMP001
    python -m simulators.run_all EMP001,EMP002,EMP003 --days 10 --url http://192.168.1.100:8000
    python -m simulators.run_all EMP001 --interactive --delay 5
"""

import argparse
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anviz import AnvizSimulator
from dahua import DahuaSimulator
from hikvision import HikvisionSimulator
from idemia import IDEMIASimulator
from sifarma import SifarmaSimulator
from suprema import SupremaSimulator
from zkteco import ZKTecoSimulator

ALL_SIMULATORS = {
    "hikvision": HikvisionSimulator,
    "zkteco": ZKTecoSimulator,
    "anviz": AnvizSimulator,
    "suprema": SupremaSimulator,
    "dahua": DahuaSimulator,
    "idemia": IDEMIASimulator,
    "sifarma": SifarmaSimulator,
}


def main():
    parser = argparse.ArgumentParser(
        description="Attendance Device Simulator — Run All Brands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m simulators.run_all EMP001
  python -m simulators.run_all EMP001,EMP002 --days 10
  python -m simulators.run_all EMP001 --brands hikvision,zkteco
  python -m simulators.run_all EMP001 --interactive --delay 5
        """,
    )
    parser.add_argument(
        "employees", help="Employee ID(s). Comma-separated for multiple."
    )
    parser.add_argument(
        "--url", default="http://127.0.0.1:8000", help="Backend base URL"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=5,
        help="Number of past days to simulate (batch mode)",
    )
    parser.add_argument(
        "--brands",
        default=",".join(ALL_SIMULATORS.keys()),
        help=f"Comma-separated brands to simulate (default: all). "
        f"Options: {', '.join(ALL_SIMULATORS.keys())}",
    )
    parser.add_argument(
        "--token",
        help="Shared device API token. If omitted, each device gets a unique token.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run interactive loop (alternates in/out every N seconds, first employee only)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Seconds between punches in interactive mode",
    )

    args = parser.parse_args()
    employee_ids = [e.strip() for e in args.employees.split(",")]
    selected_brands = [b.strip() for b in args.brands.split(",")]

    print(f"\n{'=' * 60}")
    print(f"  ATTENDANCE DEVICE SIMULATORS — OMNIBUS")
    print(f"  Backend URL : {args.url}")
    print(f"  Employees   : {', '.join(employee_ids)}")
    print(f"  Brands      : {', '.join(selected_brands)}")
    print(f"  Days        : {args.days}")
    print(
        f"  Mode        : {'Interactive' if args.interactive else f'Batch ({args.days} days)'}"
    )
    print(f"{'=' * 60}\n")

    simulators = []
    for brand_name in selected_brands:
        cls = ALL_SIMULATORS.get(brand_name.lower())
        if not cls:
            print(f"  ⚠ Unknown brand: {brand_name}. Skipping.")
            continue

        device_name = f"{cls.DEFAULT_NAME} ({brand_name.title()} Sim)"
        sim = cls(base_url=args.url, api_token=args.token, device_name=device_name)
        sim.print_info()
        simulators.append(sim)

    if not simulators:
        print("No valid simulators selected. Exiting.")
        sys.exit(1)

    if args.interactive:
        _run_interactive(simulators, employee_ids[0], args.delay)
    else:
        _run_batch_all(simulators, employee_ids, args.days)

    print(f"\n{'=' * 60}")
    print(f"  ALL SIMULATORS COMPLETE")
    print(f"{'=' * 60}\n")


def _run_batch_all(simulators, employee_ids, days):
    """Run all simulators sequentially in batch mode."""
    for sim in simulators:
        print(f"\n  --- Running {sim.BRAND_NAME} batch simulation ---")
        try:
            sim.batch_simulation(employee_ids, days=days)
        except Exception as e:
            print(f"  ✗ {sim.BRAND_NAME} failed: {e}")
        time.sleep(0.5)


def _run_interactive(simulators, employee_id, delay):
    """
    Run all simulators in parallel-ish interactive mode.
    Each simulator alternates in/out with staggered timing.
    """
    import threading

    print(f"\n  Interactive mode — {len(simulators)} simulators running simultaneously")
    print(f"  Employee: {employee_id} | Press Ctrl+C to stop\n")

    def _sim_loop(sim):
        direction = "in"
        try:
            while True:
                now = datetime.now()
                sim.push_punch(employee_id, now.isoformat(), direction)
                direction = "out" if direction == "in" else "in"
                time.sleep(
                    delay * (0.8 + 0.4 * hash(sim.BRAND_NAME) % 10 / 10)
                )  # stagger
        except KeyboardInterrupt:
            pass

    threads = []
    for sim in simulators:
        t = threading.Thread(target=_sim_loop, args=(sim,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(delay * 0.3)  # stagger starts

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n  Stopped by user.\n")


if __name__ == "__main__":
    main()
