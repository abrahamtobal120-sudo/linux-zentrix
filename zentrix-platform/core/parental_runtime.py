from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable

from core.parental import GUEST_USERS, ParentalAgent, is_admin_user


DAY_KEYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@dataclass
class SessionSnapshot:
    active: bool
    idle: bool
    state: str = ""

    @property
    def countable(self) -> bool:
        return self.active and not self.idle and self.state in {"active", "online", "closing", ""}


class SystemSessionProbe:
    """Small logind adapter kept separate so the policy engine stays testable."""

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, text=True, capture_output=True, check=False, timeout=5)

    def snapshot(self, user: str) -> SessionSnapshot:
        result = self._run("loginctl", "list-sessions", "--no-legend")
        if result.returncode != 0:
            return SessionSnapshot(active=False, idle=True, state="unavailable")

        candidate_ids: list[str] = []
        for line in result.stdout.splitlines():
            fields = line.split()
            if len(fields) >= 3 and fields[2] == user:
                candidate_ids.append(fields[0])

        best = SessionSnapshot(active=False, idle=True, state="offline")
        for session_id in candidate_ids:
            detail = self._run(
                "loginctl",
                "show-session",
                session_id,
                "-p",
                "Active",
                "-p",
                "IdleHint",
                "-p",
                "State",
                "--value",
            )
            if detail.returncode != 0:
                continue
            values = [line.strip() for line in detail.stdout.splitlines() if line.strip()]
            if len(values) < 3:
                continue
            snapshot = SessionSnapshot(
                active=values[0].lower() == "yes",
                idle=values[1].lower() == "yes",
                state=values[2].lower(),
            )
            if snapshot.countable:
                return snapshot
            if snapshot.active:
                best = snapshot
        return best

    def lock_user(self, user: str) -> bool:
        result = self._run("loginctl", "lock-user", user)
        return result.returncode == 0


class ParentalRuntime:
    def __init__(
        self,
        agent: ParentalAgent,
        probe: SystemSessionProbe | None = None,
        wall_clock: Callable[[], datetime] | None = None,
        monotonic: Callable[[], float] | None = None,
    ) -> None:
        self.agent = agent
        self.probe = probe or SystemSessionProbe()
        self.wall_clock = wall_clock or datetime.now
        self.monotonic = monotonic or time.monotonic

    def _limit_for_today(self, screen_time: dict[str, Any], now: datetime) -> int:
        by_day = screen_time.get("by_day", {}) or {}
        key = DAY_KEYS[now.weekday()]
        if key in by_day:
            return max(0, int(by_day[key]))
        return max(0, int(screen_time.get("daily_limit_minutes", 0) or 0))

    @staticmethod
    def _minute_of_day(value: str) -> int:
        hour, minute = value.split(":", 1)
        return int(hour) * 60 + int(minute)

    def _inside_window(self, current: int, start: int, end: int) -> bool:
        if start == end:
            return True
        if start < end:
            return start <= current < end
        return current >= start or current < end

    def _schedule_reason(self, screen_time: dict[str, Any], now: datetime) -> str:
        minute_now = now.hour * 60 + now.minute
        bedtime_start = str(screen_time.get("bedtime_start", "") or "")
        bedtime_end = str(screen_time.get("bedtime_end", "") or "")
        if bedtime_start and bedtime_end:
            start = self._minute_of_day(bedtime_start)
            end = self._minute_of_day(bedtime_end)
            if self._inside_window(minute_now, start, end):
                return "bedtime"

        blocked_windows = screen_time.get("blocked_hours", []) or []
        for window in blocked_windows:
            start = self._minute_of_day(str(window["start"]))
            end = self._minute_of_day(str(window["end"]))
            if self._inside_window(minute_now, start, end):
                return "blocked_schedule"

        windows = screen_time.get("allowed_hours", []) or []
        if windows:
            allowed = False
            for window in windows:
                start = self._minute_of_day(str(window["start"]))
                end = self._minute_of_day(str(window["end"]))
                if self._inside_window(minute_now, start, end):
                    allowed = True
                    break
            if not allowed:
                return "schedule"
        return ""

    @staticmethod
    def _record_usage_history(user_state: dict[str, Any], today: str, minutes: int, now: datetime) -> None:
        if minutes <= 0:
            return
        usage = user_state.setdefault("usage_by_date", {})
        if not isinstance(usage, dict):
            usage = {}
            user_state["usage_by_date"] = usage
        usage[today] = int(usage.get(today, 0) or 0) + minutes

        cutoff = now.date() - timedelta(days=35)
        for day_key in list(usage):
            try:
                day_value = datetime.fromisoformat(str(day_key)).date()
            except ValueError:
                del usage[day_key]
                continue
            if day_value < cutoff:
                del usage[day_key]

    @staticmethod
    def _weekly_used_minutes(user_state: dict[str, Any], now: datetime) -> int:
        usage = user_state.get("usage_by_date", {}) or {}
        if not isinstance(usage, dict):
            return 0
        week_start = now.date() - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        total = 0
        for day_key, minutes in usage.items():
            try:
                day_value = datetime.fromisoformat(str(day_key)).date()
            except ValueError:
                continue
            if week_start <= day_value <= week_end:
                total += max(0, int(minutes or 0))
        return total

    def tick(self) -> dict[str, Any]:
        policy, state = self.agent.load()
        now = self.wall_clock()
        mono = self.monotonic()
        today = now.date().isoformat()
        wall_epoch = now.timestamp()
        runtime = state.setdefault("runtime", {})
        runtime.setdefault("clock_anomaly", False)
        runtime.setdefault("last_wall_epoch", wall_epoch)
        runtime.setdefault("last_day", today)
        state.setdefault("users", {})

        previous_wall = float(runtime.get("last_wall_epoch", wall_epoch) or wall_epoch)
        wall_delta = wall_epoch - previous_wall
        if wall_delta < -300 or wall_delta > 36 * 3600:
            runtime["clock_anomaly"] = True
        runtime["last_wall_epoch"] = wall_epoch
        runtime["last_tick"] = now.isoformat()

        results: dict[str, Any] = {"users": {}, "clock_anomaly": runtime["clock_anomaly"]}
        screen_time = policy.screen_time or {}
        weekly_limit = max(0, int(screen_time.get("weekly_limit_minutes", 0) or 0))

        for user in policy.selected_users:
            if user in GUEST_USERS or is_admin_user(user):
                results["users"][user] = {"skipped": "protected_user"}
                continue

            user_state = state["users"].setdefault(
                user,
                {
                    "remaining_minutes": self._limit_for_today(screen_time, now),
                    "daily_used_minutes": 0,
                    "weekly_used_minutes": 0,
                    "weekly_remaining_minutes": weekly_limit,
                    "usage_by_date": {},
                    "locked": False,
                    "lock_reason": "",
                    "mode": "school" if user in policy.school_mode_users else "normal",
                },
            )
            user_state.setdefault("usage_by_date", {})
            meta = runtime.setdefault("users", {}).setdefault(
                user,
                {
                    "day": today,
                    "last_mono": mono,
                    "partial_seconds": 0.0,
                    "last_wall_epoch": wall_epoch,
                },
            )

            old_day = str(meta.get("day", today))
            day_changed = False
            if today > old_day and not runtime["clock_anomaly"]:
                limit = self._limit_for_today(screen_time, now)
                user_state["remaining_minutes"] = limit
                user_state["daily_used_minutes"] = 0
                if user_state.get("lock_reason") == "time_limit":
                    user_state["locked"] = False
                    user_state["lock_reason"] = ""
                meta["partial_seconds"] = 0.0
                meta["day"] = today
                meta["last_mono"] = mono
                day_changed = True

            weekly_used_before = self._weekly_used_minutes(user_state, now)
            if weekly_limit <= 0 or weekly_used_before < weekly_limit:
                if user_state.get("lock_reason") == "weekly_time_limit":
                    user_state["locked"] = False
                    user_state["lock_reason"] = ""

            last_mono = float(meta.get("last_mono", mono) or mono)
            elapsed = 0.0 if day_changed else max(0.0, mono - last_mono)
            meta["last_mono"] = mono
            meta["last_wall_epoch"] = wall_epoch

            reason = self._schedule_reason(screen_time, now)
            snapshot = self.probe.snapshot(user)
            counted_minutes = 0

            if snapshot.countable and not reason and not user_state.get("locked", False):
                partial = float(meta.get("partial_seconds", 0.0)) + elapsed
                counted_minutes = int(partial // 60)
                meta["partial_seconds"] = partial % 60
                if counted_minutes:
                    user_state["daily_used_minutes"] = int(user_state.get("daily_used_minutes", 0)) + counted_minutes
                    user_state["remaining_minutes"] = max(
                        0,
                        int(user_state.get("remaining_minutes", 0)) - counted_minutes,
                    )
                    self._record_usage_history(user_state, today, counted_minutes, now)
            elif not snapshot.countable:
                meta["partial_seconds"] = 0.0

            weekly_used = self._weekly_used_minutes(user_state, now)
            weekly_remaining = max(weekly_limit - weekly_used, 0) if weekly_limit > 0 else 0
            user_state["weekly_used_minutes"] = weekly_used
            user_state["weekly_remaining_minutes"] = weekly_remaining

            should_lock = False
            lock_reason = ""
            if reason:
                should_lock = True
                lock_reason = reason
            elif weekly_limit > 0 and weekly_remaining <= 0:
                should_lock = True
                lock_reason = "weekly_time_limit"
            elif int(user_state.get("remaining_minutes", 0)) <= 0:
                should_lock = True
                lock_reason = "time_limit"

            previous_locked = bool(user_state.get("locked", False))
            previous_reason = str(user_state.get("lock_reason", ""))
            if should_lock:
                user_state["locked"] = True
                user_state["lock_reason"] = lock_reason
            elif previous_locked and previous_reason in {"bedtime", "schedule", "blocked_schedule", "weekly_time_limit"}:
                user_state["locked"] = False
                user_state["lock_reason"] = ""

            results["users"][user] = {
                "active": snapshot.active,
                "idle": snapshot.idle,
                "session_state": snapshot.state,
                "counted_minutes": counted_minutes,
                "remaining_minutes": int(user_state.get("remaining_minutes", 0)),
                "daily_used_minutes": int(user_state.get("daily_used_minutes", 0)),
                "weekly_used_minutes": weekly_used,
                "weekly_remaining_minutes": weekly_remaining,
                "locked": bool(user_state.get("locked", False)),
                "lock_reason": str(user_state.get("lock_reason", "")),
            }

            if bool(user_state.get("locked", False)) and (not previous_locked or previous_reason != user_state.get("lock_reason")):
                self.agent.save_state(state)
                self.agent.set_locked(user, True, reason=str(user_state.get("lock_reason", "parental")))
                self.probe.lock_user(user)
                state = self.agent.store.load_state()
                runtime = state.setdefault("runtime", runtime)
            elif not bool(user_state.get("locked", False)) and previous_locked:
                self.agent.save_state(state)
                self.agent.set_locked(user, False)
                state = self.agent.store.load_state()
                runtime = state.setdefault("runtime", runtime)

        state["last_sync"] = now.isoformat()
        state["offline"] = True
        self.agent.save_state(state)
        return results
