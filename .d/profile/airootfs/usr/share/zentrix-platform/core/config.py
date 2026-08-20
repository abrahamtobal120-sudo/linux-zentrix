from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CoreConfig:
    name: str = "Zentrix"
    version: str = "1.0"
    telemetry_enabled: bool = False
    log_file: str = "/var/log/zentrix/core.log"
    state_file: str = "/var/lib/zentrix/state.json"
    profile_dir: str = "/usr/share/zentrix-platform/profiles"
    module_allowlist: list[str] = field(default_factory=list)


class ConfigManager:
    def __init__(self, config_path: str) -> None:
        self.config_path = Path(config_path)

    def load(self) -> CoreConfig:
        if not self.config_path.exists():
            return CoreConfig()

        raw = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        return CoreConfig(
            name=raw.get("name", "Zentrix"),
            version=str(raw.get("version", "1.0")),
            telemetry_enabled=bool(raw.get("telemetry_enabled", False)),
            log_file=raw.get("log_file", "/var/log/zentrix/core.log"),
            state_file=raw.get("state_file", "/var/lib/zentrix/state.json"),
            profile_dir=raw.get("profile_dir", "/usr/share/zentrix-platform/profiles"),
            module_allowlist=list(raw.get("module_allowlist", [])),
        )

    @staticmethod
    def load_profile(profile_dir: str, name: str) -> dict[str, Any]:
        path = Path(profile_dir) / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Profile not found: {path}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    @staticmethod
    def list_profiles(profile_dir: str) -> list[str]:
        p = Path(profile_dir)
        if not p.exists():
            return []
        return sorted([f.stem for f in p.glob("*.yaml")])
