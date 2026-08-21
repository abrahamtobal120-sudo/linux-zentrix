from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from core.parental import ParentalAgent, ParentalPolicyStore
from core.parental_runtime import ParentalRuntime, SessionSnapshot


class FakeProbe:
    def __init__(self) -> None:
        self.locked_users: list[str] = []

    def snapshot(self, _user: str) -> SessionSnapshot:
        return SessionSnapshot(active=True, idle=False, state="active")

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


def make_agent(tmp_path: Path, weekly_limit: int = 3) -> ParentalAgent:
    agent = ParentalAgent(ParentalPolicyStore(tmp_path))
    agent.save_policy_document(
        {
            "selected_users": ["kid"],
            "school_mode_users": [],
            "screen_time": {
                "daily_limit_minutes": 60,
                "weekly_limit_minutes": weekly_limit,
            },
            "apps": [],
            "internet": {"mode": "allow"},
        }
    )
    return agent


def test_weekly_limit_locks_when_total_is_reached(tmp_path: Path) -> None:
    agent = make_agent(tmp_path, weekly_limit=3)
    fake_time = FakeTime(datetime(2026, 8, 17, 18, 0, 0))  # Monday
    probe = FakeProbe()
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)

    runtime.tick()
    fake_time.advance(180)
    result = runtime.tick()

    user = result["users"]["kid"]
    assert user["weekly_used_minutes"] == 3
    assert user["weekly_remaining_minutes"] == 0
    assert user["locked"] is True
    assert user["lock_reason"] == "weekly_time_limit"


def test_weekly_limit_resets_on_new_week(tmp_path: Path) -> None:
    agent = make_agent(tmp_path, weekly_limit=2)
    fake_time = FakeTime(datetime(2026, 8, 23, 20, 0, 0))  # Sunday
    probe = FakeProbe()
    runtime = ParentalRuntime(agent, probe=probe, wall_clock=fake_time.now, monotonic=fake_time.monotonic)

    runtime.tick()
    fake_time.advance(120)
    result = runtime.tick()
    assert result["users"]["kid"]["lock_reason"] == "weekly_time_limit"

    fake_time.advance(4 * 3600)  # Monday 00:02, new week
    result = runtime.tick()
    user = result["users"]["kid"]
    assert user["weekly_used_minutes"] == 0
    assert user["weekly_remaining_minutes"] == 2
    assert user["lock_reason"] != "weekly_time_limit"
