from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from core.parental import ParentalAgent, ParentalPolicyStore
from core.parental_runtime import ParentalRuntime, SessionSnapshot


class FakeProbe:
    def __init__(self, active: bool = True, idle: bool = False) -> None:
        self.active = active
        self.idle = idle
        self.locked_users: list[str] = []

    def snapshot(self, _user: str) -> SessionSnapshot:
        return SessionSnapshot(active=self.active, idle=self.idle, state="active" if self.active else "offline")

    def lock_user(self, user: str) -> bool:
        self.locked_users.append(user)
        return True


class FakeTime:
    def __init__(self, wall: datetime) -> None:
        self.wall = wall
        self.mono = 1000.0

    def now(self) -> datetime:
        return self.wall

    def monotonic(self) -> float:
        return self.mono

    def advance(self, seconds: int) -> None:
        self.wall += timedelta(seconds=seconds)
        self.mono += seconds


def make_agent(tmp_path: Path, minutes: int = 180) -> ParentalAgent:
    agent = ParentalAgent(ParentalPolicyStore(tmp_path))
    agent.save_policy_document(
        {
            "selected_users": ["kid"],
            "school_mode_users": [],
            "screen_time": {"daily_limit_minutes": minutes},
            "apps": [],
            "internet": {"mode": "allow"},
        }
    )
    return agent


def test_parental_policy_roundtrip(tmp_path: Path) -> None:
    agent = make_agent(tmp_path)
    status = agent.status()
    assert "kid" in status.enabled_users
    policy = agent.show_policy()
    assert policy["selected_users"] == ["kid"]
    assert (tmp_path / "policy.last-good.json").exists()


def test_parental_request_time(tmp_path: Path) -> None:
    agent = make_agent(tmp_path)
    result = agent.request_extra_time(15, user="kid")
    assert result["ok"] is True
    diagnostics = agent.diagnostics()
    assert diagnostics["requests"][0]["minutes"] == 15


def test_parental_lock_and_school_mode(tmp_path: Path) -> None:
    agent = make_agent(tmp_path)
    agent.set_user_mode("kid", "school")
    agent.record_usage("kid", 180)
    state = agent.store.load_state()["users"]["kid"]
    assert state["locked"] is True
    assert state["mode"] == "school"
    assert state["lock_reason"] == "time_limit"
    assert agent.store.lock_file.exists()


def test_parental_apps_and_internet_rules(tmp_path: Path) -> None:
    agent = make_agent(tmp_path)
    agent.update_apps(
        [
            {"identifier": "/usr/bin/firefox", "action": "allow", "category": "education", "always_allowed": True},
            {"identifier": "org.gnome.Calculator.desktop", "action": "block", "category": "games"},
        ]
    )
    agent.update_internet({"mode": "pause", "allowed_domains": ["wikipedia.org"], "blocked_domains": ["youtube.com"]})
    policy = agent.show_policy()
    assert policy["apps"][0]["identifier"] == "/usr/bin/firefox"
    assert policy["internet"]["mode"] == "pause"


def test_parental_save_policy_document(tmp_path: Path) -> None:
    agent = ParentalAgent(ParentalPolicyStore(tmp_path))
    result = agent.save_policy_document(
        {
            "selected_users": ["kid"],
            "school_mode_users": ["kid"],
            "screen_time": {"daily_limit_minutes": 90},
            "apps": [],
            "internet": {"mode": "allow"},
        }
    )
    assert result["ok"] is True
    state = agent.store.load_state()["users"]["kid"]
    assert state["remaining_minutes"] == 90


def test_invalid_policy_does_not_replace_last_good(tmp_path: Path) -> None:
    agent = make_agent(tmp_path, minutes=120)
    agent.store.policy_path.write_text("{broken", encoding="utf-8")
    policy = agent.store.load_policy()
    assert policy.screen_time["daily_limit_minutes"] == 120


def test_guest_and_root_are_protected(tmp_path: Path) -> None:
    agent = ParentalAgent(ParentalPolicyStore(tmp_path))
    with pytest.raises(ValueError):
        agent.save_policy_document(
            {"selected_users": ["guest"], "screen_time": {"daily_limit_minutes": 60}, "apps": [], "internet": {"mode": "allow"}}
        )
    with pytest.raises(ValueError):
        agent.save_policy_document(
            {"selected_users": ["root"], "screen_time": {"daily_limit_minutes": 60}, "apps": [], "internet": {"mode": "allow"}}
        )


def test_runtime_counts_only_active_non_idle_time(tmp_path: Path) -> None:
    agent = make_agent(tmp_path, minutes=10)
    fake_time = FakeTime(datetime(2026, 8, 20, 18, 0, 0))
    probe = FakeProbe(active=True, idle=False)
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)

    runtime.tick()
    fake_time.advance(60)
    result = runtime.tick()
    assert result["users"]["kid"]["counted_minutes"] == 1
    assert result["users"]["kid"]["weekly_used_minutes"] == 1
    state = agent.store.load_state()["users"]["kid"]
    assert state["remaining_minutes"] == 9
    assert state["weekly_used_minutes"] == 1

    probe.idle = True
    fake_time.advance(120)
    runtime.tick()
    state = agent.store.load_state()["users"]["kid"]
    assert state["remaining_minutes"] == 9
    assert state["weekly_used_minutes"] == 1


def test_runtime_does_not_count_logged_out_or_suspended_gap(tmp_path: Path) -> None:
    agent = make_agent(tmp_path, minutes=10)
    fake_time = FakeTime(datetime(2026, 8, 20, 18, 0, 0))
    probe = FakeProbe(active=False, idle=True)
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)
    runtime.tick()
    fake_time.advance(600)
    runtime.tick()
    assert agent.store.load_state()["users"]["kid"]["remaining_minutes"] == 10


def test_runtime_bedtime_locks_controlled_user(tmp_path: Path) -> None:
    agent = ParentalAgent(ParentalPolicyStore(tmp_path))
    agent.save_policy_document(
        {
            "selected_users": ["kid"],
            "school_mode_users": [],
            "screen_time": {
                "daily_limit_minutes": 120,
                "bedtime_start": "21:00",
                "bedtime_end": "07:00",
            },
            "apps": [],
            "internet": {"mode": "allow"},
        }
    )
    fake_time = FakeTime(datetime(2026, 8, 20, 22, 0, 0))
    probe = FakeProbe()
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)
    result = runtime.tick()
    assert result["users"]["kid"]["locked"] is True
    assert result["users"]["kid"]["lock_reason"] == "bedtime"
    assert probe.locked_users == ["kid"]


def test_runtime_allowed_hours_lock_outside_range(tmp_path: Path) -> None:
    agent = ParentalAgent(ParentalPolicyStore(tmp_path))
    agent.save_policy_document(
        {
            "selected_users": ["kid"],
            "screen_time": {
                "daily_limit_minutes": 120,
                "allowed_hours": [{"start": "17:00", "end": "20:00"}],
            },
            "apps": [],
            "internet": {"mode": "allow"},
        }
    )
    fake_time = FakeTime(datetime(2026, 8, 20, 15, 30, 0))
    probe = FakeProbe()
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)
    result = runtime.tick()
    assert result["users"]["kid"]["locked"] is True
    assert result["users"]["kid"]["lock_reason"] == "schedule"


def test_runtime_blocked_hours_override_allowed_range(tmp_path: Path) -> None:
    agent = ParentalAgent(ParentalPolicyStore(tmp_path))
    agent.save_policy_document(
        {
            "selected_users": ["kid"],
            "screen_time": {
                "daily_limit_minutes": 120,
                "allowed_hours": [{"start": "07:00", "end": "22:00"}],
                "blocked_hours": [{"start": "14:00", "end": "16:00"}],
            },
            "apps": [],
            "internet": {"mode": "allow"},
        }
    )
    fake_time = FakeTime(datetime(2026, 8, 20, 15, 0, 0))
    probe = FakeProbe()
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)
    result = runtime.tick()
    assert result["users"]["kid"]["locked"] is True
    assert result["users"]["kid"]["lock_reason"] == "blocked_schedule"


def test_runtime_normal_day_change_resets_limit(tmp_path: Path) -> None:
    agent = make_agent(tmp_path, minutes=5)
    fake_time = FakeTime(datetime(2026, 8, 20, 23, 58, 0))
    probe = FakeProbe()
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)
    runtime.tick()
    fake_time.advance(60)
    runtime.tick()
    assert agent.store.load_state()["users"]["kid"]["remaining_minutes"] == 4
    fake_time.advance(120)
    runtime.tick()
    assert agent.store.load_state()["users"]["kid"]["remaining_minutes"] == 5


def test_clock_rollback_does_not_restore_time(tmp_path: Path) -> None:
    agent = make_agent(tmp_path, minutes=5)
    fake_time = FakeTime(datetime(2026, 8, 20, 18, 0, 0))
    probe = FakeProbe()
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)
    runtime.tick()
    fake_time.advance(60)
    runtime.tick()
    assert agent.store.load_state()["users"]["kid"]["remaining_minutes"] == 4

    fake_time.wall -= timedelta(hours=2)
    fake_time.mono += 60
    result = runtime.tick()
    assert result["clock_anomaly"] is True
    assert agent.store.load_state()["users"]["kid"]["remaining_minutes"] <= 4
