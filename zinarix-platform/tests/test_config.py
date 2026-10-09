from pathlib import Path

from core.config import ConfigManager


def test_config_defaults(tmp_path: Path):
    cfg = ConfigManager(str(tmp_path / "missing.yaml")).load()
    assert cfg.name == "Zinarix"
    assert cfg.version == "1.0"
    assert cfg.telemetry_enabled is False
