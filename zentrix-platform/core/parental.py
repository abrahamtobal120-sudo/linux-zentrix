from __future__ import annotations

import grp
import json
import os
import pwd
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DATA_DIR = Path("/var/lib/zentrix-parental")
DEFAULT_POLICY_FILE = DEFAULT_DATA_DIR / "policy.json"
DEFAULT_POLICY_BACKUP_FILE = DEFAULT_DATA_DIR / "policy.last-good.json"
DEFAULT_STATE_FILE = DEFAULT_DATA_DIR / "state.json"
DEFAULT_LOCK_FILE = DEFAULT_DATA_DIR / "lockscreen.json"
GUEST_USERS = {"guest", "zentrix-guest"}
ADMIN_GROUPS = {"wheel", "sudo"}


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
    weekly_used_minutes: int = 0
    locked: bool = False
    offline: bool = True
    last_sync: str = ""
    policy_path: str = str(DEFAULT_POLICY_FILE)
    state_path: str = str(DEFAULT_STATE_FILE)
    lockscreen_path: str = str(DEFAULT_LOCK_FILE)


def _parse_hhmm(value: str) -> tuple[int, int]:
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError(f"Hora inválida: {value}")
    hour, minute = (int(parts[0]), int(parts[1]))
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError(f"Hora inválida: {value}")
    return hour, minute


def is_admin_user(user: str) -> bool:
    if not user:
        return False
    try:
        account = pwd.getpwnam(user)
    except KeyError:
        return False
    if account.pw_uid == 0:
        return True
    group_names: set[str] = set()
    try:
        group_names.add(grp.getgrgid(account.pw_gid).gr_name)
    except KeyError:
        pass
    for group in grp.getgrall():
        if user in group.gr_mem:
            group_names.add(group.gr_name)
    return bool(group_names & ADMIN_GROUPS)


class ParentalPolicyStore:
    def __init__(self, data_dir: str | Path = DEFAULT_DATA_DIR) -> None:
        self.data_dir = Path(data_dir)
        self.policy_path = self.data_dir / "policy.json"
        self.policy_backup_path = self.data_dir / "policy.last-good.json"
        self.state_path = self.data_dir / "state.json"
        self.lock_file = self.data_dir / "lockscreen.json"

    def ensure(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.data_dir.chmod(0o700)
        except PermissionError:
            pass

    def _secure_write_json(self, path: Path, payload: Any) -> None:
        self.ensure()
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        try:
            tmp.chmod(0o600)
        except PermissionError:
            pass
        tmp.replace(path)
        try:
            path.chmod(0o600)
        except PermissionError:
            pass

    def _read_policy_path(self, path: Path) -> ParentalPolicy:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("La política debe ser un objeto JSON")
        return ParentalPolicy(**raw)

    def load_policy(self) -> ParentalPolicy:
        if not self.policy_path.exists():
            if self.policy_backup_path.exists():
                return self._read_policy_path(self.policy_backup_path)
            return ParentalPolicy()
        try:
            return self._read_policy_path(self.policy_path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            if self.policy_backup_path.exists():
                return self._read_policy_path(self.policy_backup_path)
            raise

    def save_policy(self, policy: ParentalPolicy) -> None:
        payload = policy.__dict__
        self._secure_write_json(self.policy_path, payload)
        self._secure_write_json(self.policy_backup_path, payload)

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"users": {}, "requests": [], "commands": [], "last_sync": "", "runtime": {}}
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return {"users": {}, "requests": [], "commands": [], "last_sync": "", "runtime": {}, "state_error": True}
        return raw if isinstance(raw, dict) else {"users": {}, "requests": [], "commands": [], "last_sync": "", "runtime": {}}

    def save_state(self, state: dict[str, Any]) -> None:
        self._secure_write_json(self.state_path, state)


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
        user_state = state.get("users", {}).get(current_user, {}) if current_user in users else {}
        return ParentalStatus(
            enabled_users=users,
            current_user=current_user,
            mode=user_state.get("mode", "normal"),
            remaining_minutes=int(user_state.get("remaining_minutes", 0)),
            daily_used_minutes=int(user_state.get("daily_used_minutes", 0)),
            weekly_used_minutes=int(user_state.get("weekly_used_minutes", 0)),
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
            "policy_backup_exists": self.store.policy_backup_path.exists(),
            "state_file_exists": self.store.state_path.exists(),
            "controlled_users": policy.selected_users,
            "requests": state.get("requests", []),
            "commands": state.get("commands", []),
            "runtime": state.get("runtime", {}),
            "lockscreen_file_exists": self.store.lock_file.exists(),
            "state_error": bool(state.get("state_error", False)),
        }

    def validate_policy_document(self, policy: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(policy, dict):
            raise ValueError("La política debe ser un objeto JSON")

        users_raw = policy.get("selected_users", [])
        if not isinstance(users_raw, list):
            raise ValueError("selected_users debe ser una lista")
        users: list[str] = []
        for raw_user in users_raw:
            user = str(raw_user).strip()
            if not user:
                continue
            if user in GUEST_USERS:
                raise ValueError("Guest Mode no puede quedar bajo control parental automáticamente")
            if is_admin_user(user):
                raise ValueError(f"El usuario administrador '{user}' no puede ser usuario controlado")
            if user not in users:
                users.append(user)

        screen_time = policy.get("screen_time", {}) or {}
        if not isinstance(screen_time, dict):
            raise ValueError("screen_time debe ser un objeto")
        daily = screen_time.get("daily_limit_minutes")
        if daily is not None and not 0 <= int(daily) <= 1440:
            raise ValueError("daily_limit_minutes debe estar entre 0 y 1440")
        by_day = screen_time.get("by_day", {}) or {}
        if not isinstance(by_day, dict):
            raise ValueError("by_day debe ser un objeto")
        for day, value in by_day.items():
            if str(day).lower() not in {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}:
                raise ValueError(f"Día inválido en by_day: {day}")
            if not 0 <= int(value) <= 1440:
                raise ValueError(f"Límite inválido para {day}")
        allowed_hours = screen_time.get("allowed_hours", []) or []
        if not isinstance(allowed_hours, list):
            raise ValueError("allowed_hours debe ser una lista")
        for window in allowed_hours:
            if not isinstance(window, dict) or "start" not in window or "end" not in window:
                raise ValueError("Cada allowed_hours necesita start y end")
            _parse_hhmm(str(window["start"]))
            _parse_hhmm(str(window["end"]))
        bedtime_start = str(screen_time.get("bedtime_start", "") or "")
        bedtime_end = str(screen_time.get("bedtime_end", "") or "")
        if bool(bedtime_start) != bool(bedtime_end):
            raise ValueError("bedtime_start y bedtime_end deben configurarse juntos")
        if bedtime_start:
            _parse_hhmm(bedtime_start)
            _parse_hhmm(bedtime_end)

        apps = policy.get("apps", []) or []
        if not isinstance(apps, list):
            raise ValueError("apps debe ser una lista")
        for app in apps:
            if not isinstance(app, dict) or not str(app.get("identifier", "")).strip():
                raise ValueError("Cada regla de app necesita identifier")
            if str(app.get("action", "allow")) not in {"allow", "block", "limit"}:
                raise ValueError("action de app debe ser allow, block o limit")

        internet = policy.get("internet", {}) or {}
        if not isinstance(internet, dict):
            raise ValueError("internet debe ser un objeto")
        if str(internet.get("mode", "allow")) not in {"allow", "pause", "filter"}:
            raise ValueError("internet.mode debe ser allow, pause o filter")

        school_users = [str(user).strip() for user in policy.get("school_mode_users", []) if str(user).strip()]
        school_users = [user for user in school_users if user in users]

        return {
            "version": int(policy.get("version", 1)),
            "selected_users": users,
            "school_mode_users": sorted(set(school_users)),
            "screen_time": screen_time,
            "apps": apps,
            "internet": internet,
        }

    def save_policy_document(self, policy: dict[str, Any]) -> dict[str, Any]:
        validated = self.validate_policy_document(policy)
        document = ParentalPolicy(
            version=validated["version"],
            selected_users=validated["selected_users"],
            school_mode_users=validated["school_mode_users"],
            screen_time=validated["screen_time"],
            apps=validated["apps"],
            internet=validated["internet"],
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
                    "weekly_used_minutes": 0,
                    "usage_by_date": {},
                    "locked": False,
                    "lock_reason": "",
                    "mode": "school" if user in document.school_mode_users else "normal",
                },
            )
        self.save_state(state)
        return {"ok": True, "updated_at": document.updated_at}

    def update_apps(self, apps: list[dict[str, Any]]) -> dict[str, Any]:
        policy = self.store.load_policy()
        payload = policy.__dict__.copy()
        payload["apps"] = apps
        self.save_policy_document(payload)
        return {"ok": True, "count": len(apps)}

    def update_internet(self, internet: dict[str, Any]) -> dict[str, Any]:
        policy = self.store.load_policy()
        payload = policy.__dict__.copy()
        payload["internet"] = internet
        self.save_policy_document(payload)
        return {"ok": True, "mode": internet.get("mode", "allow")}

    def _assert_controllable_user(self, user: str) -> None:
        policy = self.store.load_policy()
        if user not in policy.selected_users:
            raise PermissionError(f"'{user}' no está configurado como usuario controlado")
        if user in GUEST_USERS or is_admin_user(user):
            raise PermissionError(f"'{user}' no puede ser bloqueado por Zentrix Parental Control")

    def set_school_mode(self, user: str, enabled: bool) -> dict[str, Any]:
        self._assert_controllable_user(user)
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
        self._assert_controllable_user(user)
        if mode not in {"normal", "school"}:
            raise ValueError("Modo parental inválido")
        state = self.store.load_state()
        user_state = state.setdefault("users", {}).setdefault(
            user,
            {"remaining_minutes": 0, "daily_used_minutes": 0, "weekly_used_minutes": 0, "usage_by_date": {}, "locked": False, "lock_reason": "", "mode": "normal"},
        )
        user_state["mode"] = mode
        self.save_state(state)
        return {"ok": True, "user": user, "mode": mode}

    def set_locked(self, user: str, locked: bool, reason: str = "manual") -> dict[str, Any]:
        self._assert_controllable_user(user)
        state = self.store.load_state()
        user_state = state.setdefault("users", {}).setdefault(
            user,
            {"remaining_minutes": 0, "daily_used_minutes": 0, "weekly_used_minutes": 0, "usage_by_date": {}, "locked": False, "lock_reason": "", "mode": "normal"},
        )
        user_state["locked"] = locked
        user_state["lock_reason"] = reason if locked else ""
        if locked:
            self.store._secure_write_json(
                self.store.lock_file,
                {
                    "title": "ZENTRIX PARENTAL CONTROL",
                    "message": "Este dispositivo está pausado.",
                    "reason": reason,
                    "actions": ["Solicitar 15 minutos", "Solicitar 30 minutos", "Solicitar 1 hora"],
                    "user": user,
                    "updated_at": self._now_iso(),
                },
            )
        elif self.store.lock_file.exists():
            try:
                existing = json.loads(self.store.lock_file.read_text(encoding="utf-8"))
            except (OSError, ValueError, json.JSONDecodeError):
                existing = {}
            if existing.get("user") in {None, user}:
                self.store.lock_file.unlink(missing_ok=True)
        self.save_state(state)
        return {"ok": True, "user": user, "locked": locked, "reason": user_state["lock_reason"]}

    def record_usage(self, user: str, minutes: int) -> dict[str, Any]:
        self._assert_controllable_user(user)
        if minutes < 0:
            raise ValueError("minutes no puede ser negativo")
        state = self.store.load_state()
        user_state = state.setdefault("users", {}).setdefault(
            user,
            {"remaining_minutes": 0, "daily_used_minutes": 0, "weekly_used_minutes": 0, "usage_by_date": {}, "locked": False, "lock_reason": "", "mode": "normal"},
        )
        user_state["daily_used_minutes"] = int(user_state.get("daily_used_minutes", 0)) + minutes
        user_state["weekly_used_minutes"] = int(user_state.get("weekly_used_minutes", 0)) + minutes
        remaining = max(int(user_state.get("remaining_minutes", 0)) - minutes, 0)
        user_state["remaining_minutes"] = remaining
        if remaining <= 0:
            user_state["locked"] = True
            user_state["lock_reason"] = "time_limit"
        self.save_state(state)
        if user_state["locked"]:
            self.set_locked(user, True, reason="time_limit")
        return {"ok": True, "user": user, "remaining_minutes": remaining}

    def request_extra_time(self, minutes: int, user: str | None = None) -> dict[str, Any]:
        if minutes <= 0 or minutes > 1440:
            raise ValueError("La solicitud debe estar entre 1 y 1440 minutos")
        policy, state = self.load()
        target = user or state.get("current_user") or os.getenv("USER", "")
        if target not in policy.selected_users:
            raise PermissionError("Solo un usuario controlado puede solicitar tiempo adicional")
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
        return self.save_policy_document(
            {
                "selected_users": users,
                "school_mode_users": [],
                "screen_time": {
                    "daily_limit_minutes": 180,
                    "by_day": {"mon": 180, "tue": 180, "wed": 180, "thu": 180, "fri": 180},
                    "allowed_hours": [{"start": "07:00", "end": "21:00"}],
                    "bedtime_start": "21:00",
                    "bedtime_end": "07:00",
                },
                "apps": [{"identifier": "org.mozilla.firefox.desktop", "action": "allow", "always_allowed": True}],
                "internet": {"mode": "allow", "allowed_domains": ["khanacademy.org", "wikipedia.org"]},
            }
        )
