#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from api.client import ZentrixClient, run


def main() -> int:
    parser = argparse.ArgumentParser(prog="zentrix-drivers")
    parser.add_argument("--bus", choices=["system", "session"], default="system")
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()

    client = ZentrixClient(bus=args.bus)

    if "drivers" == "health":
      print(json.dumps(run(client.health()), indent=2))
    elif "drivers" == "drivers":
      print("Zentrix Driver Center CLI (phase 1): base command ready")
      print("Try: zentrixctl module info drivers --bus", args.bus)
    elif "drivers" == "repair":
      print("1. Check packages")
      print("2. Repair network")
      print("3. Check filesystem")
      print("4. Repair boot")
      print("5. Restore snapshot")
      print("6. Exit")
    else:
      print("zentrix-drivers: command scaffold ready for next phases")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
