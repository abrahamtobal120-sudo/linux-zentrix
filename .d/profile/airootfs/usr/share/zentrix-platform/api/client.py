from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from core.config import ConfigManager
from core.state import StateStore

try:
    from dbus_next.aio import MessageBus
    from dbus_next.constants import BusType
except ModuleNotFoundError:
    MessageBus = None
    BusType = None

from modules.registry import default_modules


class ZentrixClient:
    def __init__(self, bus: str = "system") -> None:
        if MessageBus is None or BusType is None:
            raise ModuleNotFoundError(
                "dbus-next is required for D-Bus mode. Use --local for the in-process backend."
            )
        self.bus = bus

    async def _iface(self):
        bus_type = BusType.SYSTEM if self.bus == "system" else BusType.SESSION
        bus = await MessageBus(bus_type=bus_type).connect()
        obj = await bus.introspect("org.zentrix.Core", "/org/zentrix/Core")
        proxy = bus.get_proxy_object("org.zentrix.Core", "/org/zentrix/Core", obj)
        return proxy.get_interface("org.zentrix.Core")

    async def ping(self) -> str:
        iface = await self._iface()
        return await iface.call_ping()

    async def status(self) -> dict:
        iface = await self._iface()
        return json.loads(await iface.call_get_status())

    async def list_profiles(self) -> list[str]:
        iface = await self._iface()
        return await iface.call_list_profiles()

    async def current_profile(self) -> str:
        iface = await self._iface()
        return await iface.call_get_current_profile()

    async def preview_profile(self, name: str) -> dict:
        iface = await self._iface()
        return json.loads(await iface.call_preview_profile(name))

    async def apply_profile(self, name: str, dry_run: bool) -> dict:
        iface = await self._iface()
        return json.loads(await iface.call_apply_profile(name, dry_run))

    async def restore_previous_profile(self, dry_run: bool) -> dict:
        iface = await self._iface()
        return json.loads(await iface.call_restore_previous_profile(dry_run))

    async def list_modules(self) -> list[str]:
        iface = await self._iface()
        return await iface.call_list_modules()

    async def module_info(self, name: str) -> dict:
        iface = await self._iface()
        return json.loads(await iface.call_module_info(name))

    async def health(self) -> dict:
        iface = await self._iface()
        return json.loads(await iface.call_health_check())

    async def history(self) -> list[dict]:
        iface = await self._iface()
        return json.loads(await iface.call_get_history())


class LocalZentrixClient:
    def __init__(self, root_dir: str | None = None) -> None:
        root = Path(root_dir) if root_dir else Path(__file__).resolve().parents[1]
        self.root = root
        self.config_mgr = ConfigManager(str(root / ".runtime" / "dev-config.yaml"))
        self.config = self.config_mgr.load()
        self.config.profile_dir = str(root / "profiles")
        self.config.state_file = str(root / ".runtime" / "state.json")
        self.config.log_file = str(root / ".runtime" / "local-client.log")
        self.state_store = StateStore(self.config.state_file)
        self.modules = default_modules()

    def _load_state(self):
        return self.state_store.load()

    def _persist(self, state) -> None:
        self.state_store.save(state)

    def _load_profile(self, profile_name: str) -> dict:
        return self.config_mgr.load_profile(self.config.profile_dir, profile_name)

    def _profile_diff(self, current_name: str, target_name: str) -> dict:
        current = self._load_profile(current_name)
        target = self._load_profile(target_name)
        keys = sorted(set(current.keys()) | set(target.keys()))
        changes = []
        for key in keys:
            if current.get(key) != target.get(key):
                changes.append({"field": key, "from": current.get(key), "to": target.get(key)})
        return {"from": current_name, "to": target_name, "changes": changes}

    def _apply_profile_internal(self, profile_name: str, dry_run: bool) -> dict:
        state = self._load_state()
        profile = self._load_profile(profile_name)
        results = {}
        warnings = []

        for name, mod in self.modules.items():
            result = mod.apply(profile, dry_run=dry_run)
            results[name] = asdict(result)
            if not result.ok:
                warnings.append(f"{name}: {result.message}")

        payload = {
            "ok": True,
            "dry_run": dry_run,
            "profile": profile_name,
            "warnings": warnings,
            "diff": self._profile_diff(state.current_profile, profile_name),
            "results": results,
        }

        if not dry_run:
            previous = state.current_profile
            previous_mode = state.active_mode
            state.previous_profile = previous
            state.previous_mode = previous_mode
            state.pending_restore = {
                "profile": previous,
                "mode": previous_mode,
                "saved_at": self.state_store.now_iso(),
            }
            state.current_profile = profile_name
            state.active_mode = profile_name
            state.history.append(
                {
                    "action": "apply-profile",
                    "from": previous,
                    "to": profile_name,
                    "time": self.state_store.now_iso(),
                    "warnings": warnings,
                    "diff": payload["diff"],
                }
            )
            self._persist(state)

        return payload

    async def ping(self) -> str:
        return "pong"

    async def status(self) -> dict:
        state = self._load_state()
        return {
            "name": self.config.name,
            "version": self.config.version,
            "profile": state.current_profile,
            "mode": state.active_mode,
            "previous_profile": state.previous_profile,
            "restorable": bool(state.pending_restore),
            "telemetry": self.config.telemetry_enabled,
            "modules": sorted(self.modules.keys()),
        }

    async def list_profiles(self) -> list[str]:
        return self.config_mgr.list_profiles(self.config.profile_dir)

    async def current_profile(self) -> str:
        return self._load_state().current_profile

    async def preview_profile(self, name: str) -> dict:
        return self._apply_profile_internal(name, True)

    async def apply_profile(self, name: str, dry_run: bool) -> dict:
        return self._apply_profile_internal(name, dry_run)

    async def restore_previous_profile(self, dry_run: bool) -> dict:
        state = self._load_state()
        if not state.pending_restore:
            return {"ok": False, "error": "No previous configuration available to restore."}

        restore_profile = state.pending_restore.get("profile")
        if not restore_profile:
            return {"ok": False, "error": "Invalid restore snapshot state."}

        payload = self._apply_profile_internal(restore_profile, dry_run)
        payload["restore"] = True
        payload["restoring_to"] = restore_profile

        if not dry_run:
            state = self._load_state()
            state.history.append(
                {
                    "action": "restore-profile",
                    "to": restore_profile,
                    "time": self.state_store.now_iso(),
                }
            )
            state.pending_restore = {}
            self._persist(state)

        return payload

    async def list_modules(self) -> list[str]:
        return sorted(self.modules.keys())

    async def module_info(self, name: str) -> dict:
        mod = self.modules.get(name)
        if mod is None:
            return {"ok": False, "error": f"unknown module: {name}"}
        return {"ok": True, "module": mod.info()}

    async def health(self) -> dict:
        state = self._load_state()
        return {
            "system_health": "Good",
            "failed_services": "",
            "snapshot": "Unknown",
            "profile": state.current_profile,
        }

    async def history(self) -> list[dict]:
        return self._load_state().history


def build_client(bus: str = "system", local: bool = False):
    if local:
        return LocalZentrixClient()
    return ZentrixClient(bus=bus)


def run(coro):
    return asyncio.run(coro)
