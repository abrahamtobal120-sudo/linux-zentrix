from __future__ import annotations

import json
import os
import secrets
import socket
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.supabase_transport import SupabaseRestClient


DEFAULT_DEVICE_STATE_DIR = Path("/var/lib/zentrix-parental-cloud")
DEVICE_FILE = DEFAULT_DEVICE_STATE_DIR / "device.json"


@dataclass
class DeviceIdentity:
    local_device_id: str
    device_name: str
    device_token: str
    cloud_device_id: str = ""
    family_id: str = ""


class DeviceIdentityStore:
    def __init__(self, path: str | Path = DEVICE_FILE) -> None:
        self.path = Path(path)

    def ensure(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.path.parent.chmod(0o700)
        except PermissionError:
            pass

    def load(self) -> DeviceIdentity | None:
        if not self.path.exists():
            return None
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return DeviceIdentity(**raw)

    def save(self, identity: DeviceIdentity) -> None:
        self.ensure()
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(identity.__dict__, indent=2), encoding="utf-8")
        try:
            tmp.chmod(0o600)
        except PermissionError:
            pass
        tmp.replace(self.path)
        try:
            self.path.chmod(0o600)
        except PermissionError:
            pass

    def get_or_create(self, device_name: str | None = None) -> DeviceIdentity:
        current = self.load()
        if current:
            return current
        hostname = socket.gethostname().strip() or "Zentrix Device"
        identity = DeviceIdentity(
            local_device_id=f"ztx-{uuid.uuid4()}",
            device_name=(device_name or hostname)[:160],
            device_token=secrets.token_urlsafe(48),
        )
        self.save(identity)
        return identity


class ZentrixParentalCloudClient:
    def __init__(
        self,
        url: str,
        publishable_key: str,
        *,
        identity_store: DeviceIdentityStore | None = None,
        access_token: str = "",
    ) -> None:
        self.transport = SupabaseRestClient(url, publishable_key, access_token=access_token)
        self.identity_store = identity_store or DeviceIdentityStore()

    def probe(self) -> dict[str, Any]:
        result = self.transport.probe()
        return {"ok": result.ok, "status": result.status, "error": result.error}

    def start_pairing(self, device_name: str | None = None) -> dict[str, Any]:
        identity = self.identity_store.get_or_create(device_name)
        pairing_code = "ZTX-" + "".join(str(secrets.randbelow(10)) for _ in range(6))
        result = self.transport.invoke_function(
            "zentrix-pairing-start",
            {
                "local_device_id": identity.local_device_id,
                "device_name": identity.device_name,
                "pairing_code": pairing_code,
                "device_token": identity.device_token,
            },
        )
        if not result.ok:
            return {"ok": False, "status": result.status, "error": result.error}
        payload = result.data or {}
        return {
            "ok": True,
            "pairing_code": payload.get("pairing_code", pairing_code),
            "expires_at": payload.get("expires_at", ""),
            "local_device_id": identity.local_device_id,
        }

    def sync(self, status: dict[str, Any], command_results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        identity = self.identity_store.get_or_create()
        result = self.transport.invoke_function(
            "zentrix-device-sync",
            {
                "local_device_id": identity.local_device_id,
                "status": status,
                "command_results": command_results or [],
            },
            headers={"x-zentrix-device-token": identity.device_token},
        )
        if not result.ok:
            return {"ok": False, "status": result.status, "error": result.error}
        payload = result.data or {}
        if payload.get("device_id"):
            identity.cloud_device_id = str(payload["device_id"])
        if payload.get("family_id"):
            identity.family_id = str(payload["family_id"])
        self.identity_store.save(identity)
        return {"ok": True, **payload}


def config_from_env() -> tuple[str, str]:
    return (
        os.environ.get("ZENTRIX_SUPABASE_URL", "").strip(),
        os.environ.get("ZENTRIX_SUPABASE_PUBLISHABLE_KEY", "").strip(),
    )
