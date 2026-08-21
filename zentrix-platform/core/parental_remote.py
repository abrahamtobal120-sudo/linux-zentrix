from __future__ import annotations

import base64
import json
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REMOTE_DATA_DIR = Path("/var/lib/zentrix-parental-remote")
CONFIG_RELATIVE_PATH = Path(".config") / "zentrix" / "parental-supabase.json"
FAMILIES_FILE = REMOTE_DATA_DIR / "families.json"
DEVICES_FILE = REMOTE_DATA_DIR / "devices.json"
PAIRINGS_FILE = REMOTE_DATA_DIR / "pairings.json"
COMMANDS_FILE = REMOTE_DATA_DIR / "commands.json"
STATE_FILE = REMOTE_DATA_DIR / "sync-state.json"


@dataclass
class RemoteFamily:
    family_id: str
    name: str
    created_at: str
    parents: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)


@dataclass
class RemoteDevice:
    device_id: str
    family_id: str
    name: str
    paired: bool = False
    paired_at: str = ""
    public_token: str = ""
    status: str = "Offline"
    last_seen: str = ""


@dataclass
class RemoteCommand:
    command_id: str
    device_id: str
    command_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    expires_at: str = ""
    executed_at: str = ""
    state: str = "queued"


@dataclass
class SupabaseConfig:
    url: str = ""
    anon_key: str = ""
    project_ref: str = ""
    family_name: str = ""
    parent_user: str = ""
    updated_at: str = ""


class SupabaseConfigStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else Path.home() / CONFIG_RELATIVE_PATH

    def load(self) -> SupabaseConfig:
        if not self.path.exists():
            return SupabaseConfig()
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return SupabaseConfig(**raw)

    def save(self, config: SupabaseConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(config.__dict__, indent=2), encoding="utf-8")
        tmp.replace(self.path)


class RemoteStore:
    def __init__(self, data_dir: str | Path = REMOTE_DATA_DIR) -> None:
        self.data_dir = Path(data_dir)
        self.families_file = self.data_dir / "families.json"
        self.devices_file = self.data_dir / "devices.json"
        self.pairings_file = self.data_dir / "pairings.json"
        self.commands_file = self.data_dir / "commands.json"
        self.state_file = self.data_dir / "sync-state.json"

    def ensure(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _save_json(self, path: Path, payload: Any) -> None:
        self.ensure()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(path)

    def load_families(self) -> dict[str, Any]:
        return self._load_json(self.families_file, {})

    def save_families(self, families: dict[str, Any]) -> None:
        self._save_json(self.families_file, families)

    def load_devices(self) -> dict[str, Any]:
        return self._load_json(self.devices_file, {})

    def save_devices(self, devices: dict[str, Any]) -> None:
        self._save_json(self.devices_file, devices)

    def load_pairings(self) -> dict[str, Any]:
        return self._load_json(self.pairings_file, {})

    def save_pairings(self, pairings: dict[str, Any]) -> None:
        self._save_json(self.pairings_file, pairings)

    def load_commands(self) -> dict[str, Any]:
        return self._load_json(self.commands_file, {"commands": [], "executed": []})

    def save_commands(self, commands: dict[str, Any]) -> None:
        self._save_json(self.commands_file, commands)

    def load_state(self) -> dict[str, Any]:
        return self._load_json(self.state_file, {"last_sync": "", "offline": True, "devices": {}})

    def save_state(self, state: dict[str, Any]) -> None:
        self._save_json(self.state_file, state)


class RemoteParentalManager:
    def __init__(self, store: RemoteStore | None = None) -> None:
        self.store = store or RemoteStore()
        self.store.ensure()
        self.config_store = SupabaseConfigStore()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def load_supabase_config(self) -> SupabaseConfig:
        return self.config_store.load()

    def save_supabase_config(self, url: str, anon_key: str, project_ref: str, family_name: str, parent_user: str) -> dict[str, Any]:
        config = SupabaseConfig(
            url=url.strip(),
            anon_key=anon_key.strip(),
            project_ref=project_ref.strip(),
            family_name=family_name.strip(),
            parent_user=parent_user.strip(),
            updated_at=self._now(),
        )
        self.config_store.save(config)
        return {"ok": True, "updated_at": config.updated_at}

    def validate_supabase_config(self, config: SupabaseConfig | None = None) -> dict[str, Any]:
        config = config or self.load_supabase_config()
        errors = []
        if not config.url.startswith("https://"):
            errors.append("Supabase URL debe comenzar con https://")
        if not config.anon_key:
            errors.append("Anon key faltante")
        if not config.project_ref:
            errors.append("Project ref faltante")
        if not config.family_name:
            errors.append("Nombre de familia faltante")
        if not config.parent_user:
            errors.append("Usuario padre faltante")
        return {"ok": not errors, "errors": errors, "config": config.__dict__}

    def _expiry(self, minutes: int = 15) -> str:
        return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()

    def create_family(self, name: str, parent_user: str) -> RemoteFamily:
        family_id = f"fam_{secrets.token_hex(4)}"
        family = RemoteFamily(family_id=family_id, name=name, created_at=self._now(), parents=[parent_user])
        families = self.store.load_families()
        families[family_id] = family.__dict__
        self.store.save_families(families)
        return family

    def create_device(self, family_id: str, name: str) -> tuple[RemoteDevice, str]:
        device_id = f"dev_{secrets.token_hex(4)}"
        pairing_code = self._generate_pairing_code()
        public_token = base64.urlsafe_b64encode(secrets.token_bytes(24)).decode().rstrip("=")
        device = RemoteDevice(device_id=device_id, family_id=family_id, name=name, public_token=public_token)
        devices = self.store.load_devices()
        devices[device_id] = device.__dict__
        self.store.save_devices(devices)

        pairings = self.store.load_pairings()
        pairings[pairing_code] = {
            "family_id": family_id,
            "device_id": device_id,
            "device_name": name,
            "issued_at": self._now(),
            "expires_at": self._expiry(10),
            "used": False,
            "public_token": public_token,
        }
        self.store.save_pairings(pairings)
        return device, pairing_code

    def _generate_pairing_code(self) -> str:
        digits = "".join(secrets.choice(string.digits) for _ in range(6))
        return f"ZTX-{digits}"

    def build_pairing_qr_payload(self, pairing_code: str, device_id: str, family_id: str) -> dict[str, Any]:
        return {
            "pairing_code": pairing_code,
            "device_id": device_id,
            "family_id": family_id,
            "purpose": "zentrix-parental-pairing",
        }

    def pair_device(self, pairing_code: str) -> dict[str, Any]:
        pairings = self.store.load_pairings()
        entry = pairings.get(pairing_code)
        if not entry:
            return {"ok": False, "error": "invalid_pairing_code"}
        if entry.get("used"):
            return {"ok": False, "error": "pairing_code_already_used"}

        expires_at = datetime.fromisoformat(entry["expires_at"])
        if expires_at < datetime.now(timezone.utc):
            return {"ok": False, "error": "pairing_code_expired"}

        devices = self.store.load_devices()
        device = devices.get(entry["device_id"])
        if not device:
            return {"ok": False, "error": "device_not_found"}

        device["paired"] = True
        device["paired_at"] = self._now()
        device["status"] = "Online"
        device["last_seen"] = self._now()
        devices[device["device_id"]] = device
        self.store.save_devices(devices)

        entry["used"] = True
        entry["paired_at"] = self._now()
        pairings[pairing_code] = entry
        self.store.save_pairings(pairings)

        return {
            "ok": True,
            "family_id": entry["family_id"],
            "device_id": device["device_id"],
            "public_token": entry["public_token"],
        }

    def queue_command(self, device_id: str, command_type: str, payload: dict[str, Any]) -> RemoteCommand:
        command = RemoteCommand(
            command_id=f"cmd_{secrets.token_hex(6)}",
            device_id=device_id,
            command_type=command_type,
            payload=payload,
            created_at=self._now(),
            expires_at=self._expiry(30),
        )
        data = self.store.load_commands()
        data.setdefault("commands", []).append(command.__dict__)
        self.store.save_commands(data)
        return command

    def list_commands(self, device_id: str | None = None) -> list[dict[str, Any]]:
        data = self.store.load_commands()
        commands = data.get("commands", [])
        if device_id:
            commands = [cmd for cmd in commands if cmd.get("device_id") == device_id]
        return commands

    def mark_executed(self, command_id: str) -> dict[str, Any]:
        data = self.store.load_commands()
        executed = set(data.get("executed", []))
        if command_id in executed:
            return {"ok": True, "duplicate": True, "command_id": command_id}
        executed.add(command_id)
        data["executed"] = sorted(executed)
        for cmd in data.get("commands", []):
            if cmd.get("command_id") == command_id:
                cmd["state"] = "executed"
                cmd["executed_at"] = self._now()
                break
        self.store.save_commands(data)
        return {"ok": True, "duplicate": False, "command_id": command_id}

    def sync_status(self, device_id: str, status: str, offline: bool = True) -> dict[str, Any]:
        state = self.store.load_state()
        state.setdefault("devices", {})[device_id] = {
            "status": status,
            "offline": offline,
            "synced_at": self._now(),
        }
        state["last_sync"] = self._now()
        state["offline"] = offline
        self.store.save_state(state)
        devices = self.store.load_devices()
        if device_id in devices:
            devices[device_id]["status"] = status
            devices[device_id]["last_seen"] = self._now()
            self.store.save_devices(devices)
        return {"ok": True, "device_id": device_id, "status": status}
