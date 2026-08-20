from pathlib import Path

from core.engine import ModuleRegistry, ZentrixEngine


def test_engine_persists_profile_changes(tmp_path: Path):
    engine = ZentrixEngine(
        state_path=str(tmp_path / "state.json"),
        profile_dir=str(tmp_path / "profiles"),
    )

    status = engine.get_status()
    assert status["profile"] == "normal"
    assert status["ready"] is True

    result = engine.set_profile("performance")
    assert result["ok"] is True
    assert result["profile"] == "performance"
    assert engine.get_status()["history"][-1]["to"] == "performance"


def test_module_registry_discovers_known_modules():
    registry = ModuleRegistry(modules_dir=Path(__file__).resolve().parents[1] / "modules")
    names = registry.list_names()
    assert "updater" in names
    assert "profiles" in names
