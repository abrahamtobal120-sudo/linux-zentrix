from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_DATA_DIR = Path("/var/lib/zentrix-parental")
DEFAULT_POLICY_FILE = DEFAULT_DATA_DIR / "policy.json"
DEFAULT_STATE_FILE = DEFAULT_DATA_DIR / "state.json"
DEFAULT_LOCK_FILE = DEFAULT_DATA_DIR / "lockscreen.json"


@dataclass
class ScreenTimeRule:
    daily_limit_minutes: int | None = None
    by_day: dict[str, int] = field(default_factory=dict)
    allowed_hours: list[dict[str, str]] = field(default_factory=list)
    bedtime_start: str = ""
    bedtime_end: str = ""


@dataclass
class AppRule:
    identifier: str
    action: str = "allow"
    daily_limit_minutes: int | None = None
    allowed_hours: list[dict[str, str]] = field(default_factory=list)
    category: str = ""
    always_allowed: bool = False


@dataclass
class InternetRule:
    mode: str = "allow"
    allowed_domains: list[str] = field(default_factory=list)
    blocked_domains: list[str] = field(default_factory=list)
    allowed_hours: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ParentalPolicy:
    version: int = 1
    selected_users: list[str] = field(default_factory=list)
    school_mode_users: list[str] = field(default_factory=list)
    screen_time: dict[str, Any] = field(default_factory=dict)
    apps: list[dict[str, Any]] = field(default_factory=list)
    internet: dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""


@dataclass
class ParentalStatus:
    enabled_users: list[str] = field(default_factory=list)
    current_user: str = ""
    mode: str = "normal"
    remaining_minutes: int = 0
    daily_used_minutes: int = 0
    locked: bool = False
    offline: bool = True
    last_sync: str = ""
    policy_path: str = str(DEFAULT_POLICY_FILE)
    state_path: str = str(DEFAULT_STATE_FILE)
    lockscreen_path: str = str(DEFAULT_LOCK_FILE)


class ParentalPolicyStore:
    def __init__(self, data_dir: str | Path = DEFAULT_DATA_DIR) -> None:
        self.data_dir = Path(data_dir)
        self.policy_path = self.data_dir / "policy.json"
        self.state_path = self.data_dir / "state.json"
        self.lock_file = self.data_dir / "lockscreen.json"

    def ensure(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_policy(self) -> ParentalPolicy:
        if not self.policy_path.exists():
            return ParentalPolicy()
        raw = json.loads(self.policy_path.read_text(encoding="utf-8"))
        return ParentalPolicy(**raw)

    def save_policy(self, policy: ParentalPolicy) -> None:
        self.ensure()
        tmp = self.policy_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(policy.__dict__, indent=2), encoding="utf-8")
        tmp.replace(self.policy_path)

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"users": {}, "requests": [], "commands": [], "last_sync": ""}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def save_state(self, state: dict[str, Any]) -> None:
        self.ensure()
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp.replace(self.state_path)


class ParentalAgent:
    def __init__(self, store: ParentalPolicyStore | None = None) -> None:
        self.store = store or ParentalPolicyStore()
        self.store.ensure()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _now_minutes(self) -> int:
        return int(datetime.now(timezone.utc).timestamp()) // 60

    def load(self) -> tuple[ParentalPolicy, dict[str, Any]]:
        return self.store.load_policy(), self.store.load_state()

    def save_policy(self, policy: ParentalPolicy) -> None:
        self.store.save_policy(policy)

    def save_state(self, state: dict[str, Any]) -> None:
        self.store.save_state(state)

    def status(self) -> ParentalStatus:
        policy, state = self.load()
        users = policy.selected_users
        current_user = state.get("current_user") or os.getenv("USER", "")
        if current_user not in users and users:
            current_user = users[0]
        user_state = state.get("users", {}).get(current_user, {})
        return ParentalStatus(
            enabled_users=users,
            current_user=current_user,
            mode=user_state.get("mode", "normal"),
            remaining_minutes=int(user_state.get("remaining_minutes", 0)),
            daily_used_minutes=int(user_state.get("daily_used_minutes", 0)),
            locked=bool(user_state.get("locked", False)),
            offline=bool(state.get("offline", True)),
            last_sync=str(state.get("last_sync", "")),
        )

    def list_users(self) -> list[str]:
        policy, _ = self.load()
        return sorted(set(policy.selected_users))

    def show_policy(self) -> dict[str, Any]:
        policy, _ = self.load()
        return policy.__dict__

    def diagnostics(self) -> dict[str, Any]:
        policy, state = self.load()
        return {
            "policy_file_exists": self.store.policy_path.exists(),
            "state_file_exists": self.store.state_path.exists(),
            "controlled_users": policy.selected_users,
            "requests": state.get("requests", []),
            "commands": state.get("commands", []),
            "lockscreen_file_exists": self.store.lock_file.exists(),
        }

    def save_policy_document(self, policy: dict[str, Any]) -> dict[str, Any]:
        document = ParentalPolicy(
            version=int(policy.get("version", 1)),
            selected_users=list(policy.get("selected_users", [])),
            school_mode_users=list(policy.get("school_mode_users", [])),
            screen_time=dict(policy.get("screen_time", {})),
            apps=list(policy.get("apps", [])),
            internet=dict(policy.get("internet", {})),
            updated_at=self._now_iso(),
        )
        self.save_policy(document)
        state = self.store.load_state()
        state.setdefault("users", {})
        for user in document.selected_users:
            state["users"].setdefault(
                user,
                {
                    "remaining_minutes": int(document.screen_time.get("daily_limit_minutes", 0) or 0),
                    "daily_used_minutes": 0,
                    "locked": False,
                    "mode": "school" if user in document.school_mode_users else "normal",
                },
            )
        self.save_state(state)
        return {"ok": True, "updated_at": document.updated_at}

    def update_apps(self, apps: list[dict[str, Any]]) -> dict[str, Any]:
        policy = self.store.load_policy()
        policy.apps = apps
        policy.updated_at = self._now_iso()
        self.save_policy(policy)
        return {"ok": True, "count": len(apps)}

    def update_internet(self, internet: dict[str, Any]) -> dict[str, Any]:
        policy = self.store.load_policy()
        policy.internet = internet
        policy.updated_at = self._now_iso()
        self.save_policy(policy)
        return {"ok": True, "mode": internet.get("mode", "allow")}

    def set_school_mode(self, user: str, enabled: bool) -> dict[str, Any]:
        policy = self.store.load_policy()
        users = set(policy.school_mode_users)
        if enabled:
            users.add(user)
        else:
            users.discard(user)
        policy.school_mode_users = sorted(users)
        policy.updated_at = self._now_iso()
        self.save_policy(policy)
        return self.set_user_mode(user, "school" if enabled else "normal")

    def set_user_mode(self, user: str, mode: str) -> dict[str, Any]:
        state = self.store.load_state()
        user_state = state.setdefault("users", {}).setdefault(
            user,
            {"remaining_minutes": 0, "daily_used_minutes": 0, "locked": False, "mode": "normal"},
        )
        user_state["mode"] = mode
        self.save_state(state)
        return {"ok": True, "user": user, "mode": mode}

    def set_locked(self, user: str, locked: bool) -> dict[str, Any]:
        state = self.store.load_state()
        user_state = state.setdefault("users", {}).setdefault(
            user,
            {"remaining_minutes": 0, "daily_used_minutes": 0, "locked": False, "mode": "normal"},
        )
        user_state["locked"] = locked
        if locked:
            self.store.lock_file.write_text(
                json.dumps(
                    {
                        "title": "ZENTRIX PARENTAL CONTROL",
                        "message": "Tiempo terminado.",
                        "actions": ["Solicitar 15 minutos", "Solicitar 30 minutos", "Solicitar 1 hora"],
                        "user": user,
                        "updated_at": self._now_iso(),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        elif self.store.lock_file.exists():
            self.store.lock_file.unlink()
        self.save_state(state)
        return {"ok": True, "user": user, "locked": locked}

    def record_usage(self, user: str, minutes: int) -> dict[str, Any]:
        state = self.store.load_state()
        user_state = state.setdefault("users", {}).setdefault(
            user,
            {"remaining_minutes": 0, "daily_used_minutes": 0, "locked": False, "mode": "normal"},
        )
        user_state["daily_used_minutes"] = int(user_state.get("daily_used_minutes", 0)) + minutes
        remaining = max(int(user_state.get("remaining_minutes", 0)) - minutes, 0)
        user_state["remaining_minutes"] = remaining
        if remaining <= 0:
            user_state["locked"] = True
        self.save_state(state)
        if user_state["locked"]:
            self.set_locked(user, True)
        return {"ok": True, "user": user, "remaining_minutes": remaining}

    def request_extra_time(self, minutes: int, user: str | None = None) -> dict[str, Any]:
        policy, state = self.load()
        target = user or state.get("current_user") or os.getenv("USER", "")
        state.setdefault("requests", []).append(
            {
                "type": "extra_time",
                "user": target,
                "minutes": minutes,
                "state": "pending",
                "requested_at": self._now_minutes(),
            }
        )
        self.save_state(state)
        return {"ok": True, "user": target, "minutes": minutes, "policy_version": policy.version}

    def apply_demo_policy(self, users: list[str]) -> dict[str, Any]:
        policy = ParentalPolicy(
            selected_users=users,
            school_mode_users=[],
            screen_time={"daily_limit_minutes": 180, "by_day": {"mon": 180, "tue": 180, "wed": 180, "thu": 180, "fri": 180}, "allowed_hours": [{"start": "07:00", "end": "21:00"}], "bedtime_start": "21:00", "bedtime_end": "07:00"},
            apps=[{"identifier": "org.mozilla.firefox.desktop", "action": "allow", "always_allowed": True}],
            internet={"mode": "allow", "allowed_domains": ["khanacademy.org", "wikipedia.org"]},
            updated_at=self._now_iso(),
        )
        self.save_policy(policy)
        state = self.store.load_state()
        state.setdefault("users", {})
        for user in users:
            state["users"].setdefault(
                user,
                {"remaining_minutes": 180, "daily_used_minutes": 0, "locked": False, "mode": "normal"},
            )
        self.save_state(state)
        return {"ok": True, "users": users}
