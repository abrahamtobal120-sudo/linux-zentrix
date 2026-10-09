#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from api.client import ZinarixClient, run


def main() -> int:
    parser = argparse.ArgumentParser(prog="zinarix-repair")
    parser.add_argument("--bus", choices=["system", "session"], default="system")
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()

    client = ZinarixClient(bus=args.bus)

    if "repair" == "health":
      print(json.dumps(run(client.health()), indent=2))
    elif "repair" == "drivers":
      print("Zinarix Driver Center CLI (phase 1): base command ready")
      print("Try: zinarixctl module info drivers --bus", args.bus)
    elif "repair" == "repair":
      print("1. Check packages")
      print("2. Repair network")
      print("3. Check filesystem")
      print("4. Repair boot")
      print("5. Restore snapshot")
      print("6. Exit")
    else:
      print("zinarix-repair: command scaffold ready for next phases")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
