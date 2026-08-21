from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.parental import ParentalAgent


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zentrix-parental", description="Zentrix Parental Control CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")

    user = sub.add_parser("user")
    user_sub = user.add_subparsers(dest="user_cmd", required=True)
    user_sub.add_parser("list")

    policy = sub.add_parser("policy")
    policy_sub = policy.add_subparsers(dest="policy_cmd", required=True)
    policy_sub.add_parser("show")

    apps = sub.add_parser("apps")
    apps_sub = apps.add_subparsers(dest="apps_cmd", required=True)
    apps_sub.add_parser("show")
    apps_set = apps_sub.add_parser("set")
    apps_set.add_argument("json_payload", help="JSON array of app rules")

    internet = sub.add_parser("internet")
    internet_sub = internet.add_subparsers(dest="internet_cmd", required=True)
    internet_sub.add_parser("show")
    internet_set = internet_sub.add_parser("set")
    internet_set.add_argument("json_payload", help="JSON object of internet rules")

    school = sub.add_parser("school")
    school_sub = school.add_subparsers(dest="school_cmd", required=True)
    school_on = school_sub.add_parser("enable")
    school_on.add_argument("user")
    school_off = school_sub.add_parser("disable")
    school_off.add_argument("user")

    import_p = sub.add_parser("import")
    import_p.add_argument("path", help="Path to a JSON policy file")

    sub.add_parser("diagnostics")

    req = sub.add_parser("request-time")
    req.add_argument("minutes", type=int)
    req.add_argument("--user", default="")

    demo = sub.add_parser("demo-policy")
    demo.add_argument("users", nargs="+", help="Users to control")

    return p


def main() -> int:
    args = parser().parse_args()
    agent = ParentalAgent()

    if args.cmd == "status":
        print(json.dumps(agent.status().__dict__, indent=2))
        return 0

    if args.cmd == "user" and args.user_cmd == "list":
        print("\n".join(agent.list_users()))
        return 0

    if args.cmd == "policy" and args.policy_cmd == "show":
        print(json.dumps(agent.show_policy(), indent=2))
        return 0

    if args.cmd == "apps":
        if args.apps_cmd == "show":
            print(json.dumps(agent.show_policy().get("apps", []), indent=2))
            return 0
        if args.apps_cmd == "set":
            payload = json.loads(args.json_payload)
            print(json.dumps(agent.update_apps(payload), indent=2))
            return 0

    if args.cmd == "internet":
        if args.internet_cmd == "show":
            print(json.dumps(agent.show_policy().get("internet", {}), indent=2))
            return 0
        if args.internet_cmd == "set":
            payload = json.loads(args.json_payload)
            print(json.dumps(agent.update_internet(payload), indent=2))
            return 0

    if args.cmd == "school":
        if args.school_cmd == "enable":
            print(json.dumps(agent.set_school_mode(args.user, True), indent=2))
            return 0
        if args.school_cmd == "disable":
            print(json.dumps(agent.set_school_mode(args.user, False), indent=2))
            return 0

    if args.cmd == "import":
        from pathlib import Path

        payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
        print(json.dumps(agent.save_policy_document(payload), indent=2))
        return 0

    if args.cmd == "diagnostics":
        print(json.dumps(agent.diagnostics(), indent=2))
        return 0

    if args.cmd == "request-time":
        print(json.dumps(agent.request_extra_time(args.minutes, user=args.user or None), indent=2))
        return 0

    if args.cmd == "demo-policy":
        print(json.dumps(agent.apply_demo_policy(args.users), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
