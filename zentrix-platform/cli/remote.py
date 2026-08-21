from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.parental_remote import RemoteParentalManager


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zentrix-parental-remote", description="Zentrix Parental Remote Stage 2")
    sub = p.add_subparsers(dest="cmd", required=True)

    fam = sub.add_parser("family-create")
    fam.add_argument("name")
    fam.add_argument("parent_user")

    dev = sub.add_parser("device-create")
    dev.add_argument("family_id")
    dev.add_argument("name")

    cfg = sub.add_parser("config")
    cfg_sub = cfg.add_subparsers(dest="config_cmd", required=True)
    cfg_show = cfg_sub.add_parser("show")
    cfg_set = cfg_sub.add_parser("set")
    cfg_set.add_argument("url")
    cfg_set.add_argument("anon_key")
    cfg_set.add_argument("project_ref")
    cfg_set.add_argument("family_name")
    cfg_set.add_argument("parent_user")
    cfg_sub.add_parser("validate")

    pair = sub.add_parser("pair")
    pair.add_argument("pairing_code")

    cmd = sub.add_parser("command")
    cmd.add_argument("device_id")
    cmd.add_argument("command_type")
    cmd.add_argument("payload_json")

    sync = sub.add_parser("sync-status")
    sync.add_argument("device_id")
    sync.add_argument("status")
    sync.add_argument("--online", action="store_true")

    list_cmd = sub.add_parser("command-list")
    list_cmd.add_argument("--device-id", default="")

    exec_cmd = sub.add_parser("mark-executed")
    exec_cmd.add_argument("command_id")

    return p


def main() -> int:
    args = parser().parse_args()
    manager = RemoteParentalManager()

    if args.cmd == "family-create":
        family = manager.create_family(args.name, args.parent_user)
        print(json.dumps(family.__dict__, indent=2))
        return 0

    if args.cmd == "device-create":
        device, pairing_code = manager.create_device(args.family_id, args.name)
        payload = manager.build_pairing_qr_payload(pairing_code, device.device_id, device.family_id)
        print(json.dumps({"device": device.__dict__, "pairing_code": pairing_code, "qr_payload": payload}, indent=2))
        return 0

    if args.cmd == "config":
        if args.config_cmd == "show":
            print(json.dumps(manager.load_supabase_config().__dict__, indent=2))
            return 0
        if args.config_cmd == "set":
            print(json.dumps(manager.save_supabase_config(args.url, args.anon_key, args.project_ref, args.family_name, args.parent_user), indent=2))
            return 0
        if args.config_cmd == "validate":
            print(json.dumps(manager.validate_supabase_config(), indent=2))
            return 0

    if args.cmd == "pair":
        print(json.dumps(manager.pair_device(args.pairing_code), indent=2))
        return 0

    if args.cmd == "command":
        payload = json.loads(args.payload_json)
        command = manager.queue_command(args.device_id, args.command_type, payload)
        print(json.dumps(command.__dict__, indent=2))
        return 0

    if args.cmd == "sync-status":
        print(json.dumps(manager.sync_status(args.device_id, args.status, offline=not args.online), indent=2))
        return 0

    if args.cmd == "command-list":
        print(json.dumps(manager.list_commands(args.device_id or None), indent=2))
        return 0

    if args.cmd == "mark-executed":
        print(json.dumps(manager.mark_executed(args.command_id), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
