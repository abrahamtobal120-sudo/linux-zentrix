from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from dbus_next.service import ServiceInterface, method

from core.config import ConfigManager, CoreConfig
from core.state import CoreState, StateStore
from modules.registry import default_modules


class ZentrixService(ServiceInterface):
    def __init__(
        self,
        config: CoreConfig,
        config_mgr: ConfigManager,
        state_store: StateStore,
        state: CoreState,
        logger,
    ) -> None:
        super().__init__("org.zentrix.Core")
        self.config = config
        self.config_mgr = config_mgr
        self.state_store = state_store
        self.state = state
        self.logger = logger
        self.modules = default_modules()

    def _load_profile(self, profile_name: str) -> dict[str, Any]:
        return self.config_mgr.load_profile(self.config.profile_dir, profile_name)

    def _profile_diff(self, current_name: str, target_name: str) -> dict[str, Any]:
        current = self._load_profile(current_name)
        target = self._load_profile(target_name)
        keys = sorted(set(current.keys()) | set(target.keys()))
        changes = []
        for key in keys:
            if current.get(key) != target.get(key):
                changes.append(
                    {
                        "field": key,
                        "from": current.get(key),
                        "to": target.get(key),
                    }
                )
        return {
            "from": current_name,
            "to": target_name,
            "changes": changes,
        }

    def _apply_profile_internal(self, profile_name: str, dry_run: bool) -> dict[str, Any]:
        profile = self._load_profile(profile_name)

        plans = {}
        warnings = []
        for name, mod in self.modules.items():
            result = mod.apply(profile, dry_run=dry_run)
            plans[name] = asdict(result)
            if not result.ok:
                warnings.append(f"{name}: {result.message}")

        payload = {
            "ok": True,
            "dry_run": dry_run,
            "profile": profile_name,
            "warnings": warnings,
            "diff": self._profile_diff(self.state.current_profile, profile_name),
            "results": plans,
        }

        if not dry_run:
            previous = self.state.current_profile
            previous_mode = self.state.active_mode
            self.state.previous_profile = previous
            self.state.previous_mode = previous_mode
            self.state.pending_restore = {
                "profile": previous,
                "mode": previous_mode,
                "saved_at": self.state_store.now_iso(),
            }
            self.state.current_profile = profile_name
            self.state.active_mode = profile_name
            self.state.history.append(
                {
                    "action": "apply-profile",
                    "from": previous,
                    "to": profile_name,
                    "time": self.state_store.now_iso(),
                    "warnings": warnings,
                    "diff": payload["diff"],
                }
            )
            self._persist()

        return payload

    def _persist(self) -> None:
        self.state_store.save(self.state)

    @method()
    def Ping(self) -> 's':
        return "pong"

    @method()
    def ListProfiles(self) -> 'as':
        return self.config_mgr.list_profiles(self.config.profile_dir)

    @method()
    def GetCurrentProfile(self) -> 's':
        return self.state.current_profile

    @method()
    def ListModules(self) -> 'as':
        return sorted(self.modules.keys())

    @method()
    def ModuleInfo(self, name: 's') -> 's':
        mod = self.modules.get(name)
        if mod is None:
            return json.dumps({"ok": False, "error": f"unknown module: {name}"})
        return json.dumps({"ok": True, "module": mod.info()})

    @method()
    def GetStatus(self) -> 's':
        payload = {
            "name": self.config.name,
            "version": self.config.version,
            "profile": self.state.current_profile,
            "mode": self.state.active_mode,
            "previous_profile": self.state.previous_profile,
            "restorable": bool(self.state.pending_restore),
            "telemetry": self.config.telemetry_enabled,
            "modules": sorted(self.modules.keys()),
        }
        return json.dumps(payload)

    @method()
    def GetHistory(self) -> 's':
        return json.dumps(self.state.history)

    @method()
    def PreviewProfile(self, profile_name: 's') -> 's':
        try:
            payload = self._apply_profile_internal(profile_name, True)
        except FileNotFoundError as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        return json.dumps(payload)

    @method()
    def ApplyProfile(self, profile_name: 's', dry_run: 'b') -> 's':
        try:
            payload = self._apply_profile_internal(profile_name, dry_run)
        except FileNotFoundError as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        return json.dumps(payload)

    @method()
    def RestorePreviousProfile(self, dry_run: 'b') -> 's':
        if not self.state.pending_restore:
            return json.dumps({"ok": False, "error": "No previous configuration available to restore."})

        restore_profile = self.state.pending_restore.get("profile")
        if not restore_profile:
            return json.dumps({"ok": False, "error": "Invalid restore snapshot state."})

        try:
            payload = self._apply_profile_internal(restore_profile, dry_run)
        except FileNotFoundError as exc:
            return json.dumps({"ok": False, "error": str(exc)})

        payload["restore"] = True
        payload["restoring_to"] = restore_profile

        if not dry_run:
            self.state.history.append(
                {
                    "action": "restore-profile",
                    "to": restore_profile,
                    "time": self.state_store.now_iso(),
                }
            )
            self.state.pending_restore = {}
            self._persist()

        return json.dumps(payload)

    @method()
    def HealthCheck(self) -> 's':
        failed_services = ""
        payload = {
            "system_health": "Good",
            "failed_services": failed_services,
            "snapshot": "Unknown",
            "profile": self.state.current_profile,
        }
        return json.dumps(payload)
