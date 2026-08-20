#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.client import build_client, run


MODES = ["eco", "normal", "performance", "gaming", "creator", "security", "school", "focus", "dev"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zentrix-mode", description="Zentrix mode manager")
    p.add_argument("--bus", choices=["system", "session"], default="system")
    p.add_argument("--local", action="store_true", help="Run against the in-process development backend")
    p.add_argument("action", choices=["status", "restore", "history", *MODES])
    p.add_argument("--dry-run", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    client = build_client(bus=args.bus, local=args.local)

    if args.action == "status":
        status = run(client.status())
        print(f"Current profile: {status.get('profile', 'unknown')}")
        print(f"Power profile: {status.get('mode', 'unknown')}")
        print(f"Previous profile: {status.get('previous_profile', 'none') or 'none'}")
        print(f"Restore available: {'Yes' if status.get('restorable') else 'No'}")
        print("Gaming optimization: Disabled")
        print("Creator services: Disabled")
        return 0

    if args.action == "restore":
        result = run(client.restore_previous_profile(args.dry_run))
        print(json.dumps(result, indent=2))
        return 0

    if args.action == "history":
        result = run(client.history())
        print(json.dumps(result, indent=2))
        return 0

    result = run(client.apply_profile(args.action, args.dry_run))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
