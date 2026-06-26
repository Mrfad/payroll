#!/usr/bin/env python
"""
Convenience entry-point script to run any device simulator from the command line
without needing the -m flag.

Usage:
    python simulators/simulate.py hikvision EMP001 --batch
    python simulators/simulate.py zkteco EMP001 --interactive --delay 3
    python simulators/simulate.py all EMP001,EMP002 --days 10
    python simulators/simulate.py list
"""

import os
import sys

# Ensure the project root is on sys.path so base.py imports work
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from simulators.run_all import ALL_SIMULATORS
from simulators.run_all import main as run_all_main


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    brand_arg = sys.argv[1].lower()

    if brand_arg == "list":
        print("Available simulators:")
        for name, cls in ALL_SIMULATORS.items():
            print(f"  {name:15s}  {cls.BRAND_NAME} ({cls.DEVICE_TYPE})")
        sys.exit(0)

    if brand_arg == "all":
        # Delegate to run_all, stripping the 'all' arg
        sys.argv.pop(1)
        run_all_main()
        return

    cls = ALL_SIMULATORS.get(brand_arg)
    if not cls:
        print(f"Unknown brand: {brand_arg}")
        print(f"Available: {', '.join(ALL_SIMULATORS.keys())}, 'all', 'list'")
        sys.exit(1)

    # Strip the brand from argv so cli_run's argparse gets clean args
    sys.argv.pop(1)
    sys.argv[0] = f"simulate.py {brand_arg}"

    from simulators.base import cli_run

    cli_run(cls)


if __name__ == "__main__":
    main()
