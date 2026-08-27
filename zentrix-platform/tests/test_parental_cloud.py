from __future__ import annotations

from pathlib import Path

from core.parental_cloud import DeviceIdentityStore


def test_device_identity_is_persistent_and_private(tmp_path: Path) -> None:
    path = tmp_path / "device.json"
    store = DeviceIdentityStore(path)

    first = store.get_or_create("Test-PC")
    second = store.get_or_create("Ignored-Name")

    assert first.local_device_id.startswith("ztx-")
    assert len(first.device_token) >= 32
    assert second.local_device_id == first.local_device_id
    assert second.device_token == first.device_token
    assert second.device_name == "Test-PC"
    assert path.stat().st_mode & 0o777 == 0o600
