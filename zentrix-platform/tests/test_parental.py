from __future__ import annotations

from pathlib import Path

from core.parental import ParentalAgent, ParentalPolicyStore


def test_parental_policy_roundtrip(tmp_path: Path) -> None:
    store = ParentalPolicyStore(tmp_path)
    agent = ParentalAgent(store)
    agent.apply_demo_policy(["kid"])

    status = agent.status()
    assert "kid" in status.enabled_users
    assert status.remaining_minutes == 180

    policy = agent.show_policy()
    assert policy["selected_users"] == ["kid"]


def test_parental_request_time(tmp_path: Path) -> None:
    store = ParentalPolicyStore(tmp_path)
    agent = ParentalAgent(store)
    agent.apply_demo_policy(["kid"])

    result = agent.request_extra_time(15, user="kid")
    assert result["ok"] is True
    diagnostics = agent.diagnostics()
    assert diagnostics["requests"][0]["minutes"] == 15


def test_parental_lock_and_school_mode(tmp_path: Path) -> None:
    store = ParentalPolicyStore(tmp_path)
    agent = ParentalAgent(store)
    agent.apply_demo_policy(["kid"])

    agent.set_user_mode("kid", "school")
    agent.record_usage("kid", 180)

    status = agent.status()
    assert status.locked is True
    assert status.mode in {"school", "normal"}
    assert store.lock_file.exists()


def test_parental_apps_and_internet_rules(tmp_path: Path) -> None:
    store = ParentalPolicyStore(tmp_path)
    agent = ParentalAgent(store)
    agent.apply_demo_policy(["kid"])

    agent.update_apps([
        {"identifier": "/usr/bin/firefox", "action": "allow", "category": "education", "always_allowed": True},
        {"identifier": "org.gnome.Calculator.desktop", "action": "block", "category": "games"},
    ])
    agent.update_internet({"mode": "pause", "allowed_domains": ["wikipedia.org"], "blocked_domains": ["youtube.com"]})
    policy = agent.show_policy()

    assert policy["apps"][0]["identifier"] == "/usr/bin/firefox"
    assert policy["internet"]["mode"] == "pause"


def test_parental_save_policy_document(tmp_path: Path) -> None:
    store = ParentalPolicyStore(tmp_path)
    agent = ParentalAgent(store)
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
    assert agent.status().remaining_minutes == 90
