from api.client import LocalZentrixClient, run


def test_local_client_applies_and_restores_profile(tmp_path):
    client = LocalZentrixClient(root_dir=str(tmp_path))
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    (profiles_dir / "normal.yaml").write_text(
        "name: normal\nsummary: Balanced\npackages: []\nservices:\n  enable: []\n  disable: []\n",
        encoding="utf-8",
    )
    (profiles_dir / "performance.yaml").write_text(
        "name: performance\nsummary: Fast\npackages: []\nservices:\n  enable: []\n  disable: []\n",
        encoding="utf-8",
    )

    status = run(client.status())
    assert status["profile"] == "normal"

    result = run(client.apply_profile("performance", False))
    assert result["ok"] is True
    assert result["profile"] == "performance"

    restored = run(client.restore_previous_profile(False))
    assert restored["ok"] is True
    assert restored["restoring_to"] == "normal"