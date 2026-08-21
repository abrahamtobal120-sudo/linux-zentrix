#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.client import build_client, run


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zentrixctl", description="Zentrix Core CLI")
    p.add_argument("--bus", choices=["system", "session"], default="system")
    p.add_argument("--local", action="store_true", help="Run against the in-process development backend")

    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ping")
    sub.add_parser("status")
    sub.add_parser("health")

    parental = sub.add_parser("parental")
    parental_sub = parental.add_subparsers(dest="parental_cmd", required=True)
    parental_sub.add_parser("status")

    parental_user = parental_sub.add_parser("user")
    parental_user_sub = parental_user.add_subparsers(dest="user_cmd", required=True)
    parental_user_sub.add_parser("list")

    parental_policy = parental_sub.add_parser("policy")
    parental_policy_sub = parental_policy.add_subparsers(dest="policy_cmd", required=True)
    parental_policy_sub.add_parser("show")

    parental_sub.add_parser("diagnostics")

    parental_request = parental_sub.add_parser("request-time")
    parental_request.add_argument("minutes", type=int)
    parental_request.add_argument("--user", default="")

    prof = sub.add_parser("profile")
    prof_sub = prof.add_subparsers(dest="profile_cmd", required=True)
    prof_sub.add_parser("list")
    apply_p = prof_sub.add_parser("apply")
    apply_p.add_argument("name")
    apply_p.add_argument("--dry-run", action="store_true")

    mod = sub.add_parser("module")
    mod_sub = mod.add_subparsers(dest="module_cmd", required=True)
    mod_sub.add_parser("list")
    mod_info = mod_sub.add_parser("info")
    mod_info.add_argument("name")

    return p


def main() -> int:
    args = parser().parse_args()
    client = build_client(bus=args.bus, local=args.local)

    if args.cmd == "ping":
        print(run(client.ping()))
        return 0

    if args.cmd == "status":
        print(json.dumps(run(client.status()), indent=2))
        return 0

    if args.cmd == "health":
        print(json.dumps(run(client.health()), indent=2))
        return 0

    if args.cmd == "parental":
        from core.parental import ParentalAgent

        agent = ParentalAgent()

        if args.parental_cmd == "status":
            print(json.dumps(agent.status().__dict__, indent=2))
            return 0

        if args.parental_cmd == "user" and args.user_cmd == "list":
            print("\n".join(agent.list_users()))
            return 0

        if args.parental_cmd == "policy" and args.policy_cmd == "show":
            print(json.dumps(agent.show_policy(), indent=2))
            return 0

        if args.parental_cmd == "diagnostics":
            print(json.dumps(agent.diagnostics(), indent=2))
            return 0

        if args.parental_cmd == "request-time":
            print(json.dumps(agent.request_extra_time(args.minutes, user=args.user or None), indent=2))
            return 0

    if args.cmd == "profile":
        if args.profile_cmd == "list":
            print("\n".join(run(client.list_profiles())))
            return 0
        if args.profile_cmd == "apply":
            result = run(client.apply_profile(args.name, args.dry_run))
            print(json.dumps(result, indent=2))
            return 0

    if args.cmd == "module":
        if args.module_cmd == "list":
            print("\n".join(run(client.list_modules())))
            return 0
        if args.module_cmd == "info":
            print(json.dumps(run(client.module_info(args.name)), indent=2))
            return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
