from __future__ import annotations

from pathlib import Path

from core.parental_remote import RemoteParentalManager, RemoteStore


def test_remote_pairing_and_one_time_code(tmp_path: Path) -> None:
    manager = RemoteParentalManager(RemoteStore(tmp_path))
    family = manager.create_family("Family", "parent")
    device, pairing_code = manager.create_device(family.family_id, "Abraham-PC")

    payload = manager.build_pairing_qr_payload(pairing_code, device.device_id, family.family_id)
    assert payload["pairing_code"] == pairing_code

    pair_result = manager.pair_device(pairing_code)
    assert pair_result["ok"] is True
    assert manager.pair_device(pairing_code)["ok"] is False


def test_remote_command_queue_and_dedup(tmp_path: Path) -> None:
    manager = RemoteParentalManager(RemoteStore(tmp_path))
    family = manager.create_family("Family", "parent")
    device, _ = manager.create_device(family.family_id, "Abraham-PC")

    command = manager.queue_command(device.device_id, "extra_time", {"minutes": 15})
    assert manager.mark_executed(command.command_id)["duplicate"] is False
    assert manager.mark_executed(command.command_id)["duplicate"] is True


def test_remote_status_sync(tmp_path: Path) -> None:
    manager = RemoteParentalManager(RemoteStore(tmp_path))
    family = manager.create_family("Family", "parent")
    device, _ = manager.create_device(family.family_id, "Abraham-PC")

    result = manager.sync_status(device.device_id, "School Mode", offline=False)
    assert result["status"] == "School Mode"


def test_supabase_config_roundtrip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    manager = RemoteParentalManager(RemoteStore(tmp_path))
    save = manager.save_supabase_config(
        "https://example.supabase.co",
        "anon-key",
        "example",
        "Familia Zentrix",
        "parent",
    )
    assert save["ok"] is True
    validation = manager.validate_supabase_config()
    assert validation["ok"] is True