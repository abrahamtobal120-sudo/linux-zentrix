from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ZentrixEngine:
    def __init__(self, state_path: str = "/var/lib/zentrix/state.json", profile_dir: str = "/usr/share/zentrix-platform/profiles") -> None:
        self.state_path = Path(state_path)
        self.profile_dir = Path(profile_dir)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                return {"profile": "normal", "history": []}
        return {"profile": "normal", "history": []}

    def save(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def get_status(self) -> dict[str, Any]:
        return {
            "profile": self.state.get("profile", "normal"),
            "history": self.state.get("history", []),
            "ready": True,
        }

    def set_profile(self, profile: str) -> dict[str, Any]:
        previous = self.state.get("profile", "normal")
        self.state["profile"] = profile
        self.state.setdefault("history", []).append({"from": previous, "to": profile})
        self.save()
        return {"ok": True, "profile": profile, "from": previous}


class ModuleRegistry:
    def __init__(self, modules_dir: Path | str) -> None:
        self.modules_dir = Path(modules_dir)

    def discover(self) -> list[Path]:
        if not self.modules_dir.exists():
            return []

        modules: list[Path] = []
        for entry in sorted(self.modules_dir.iterdir()):
            if entry.is_dir() and (entry / "__init__.py").exists():
                modules.append(entry)
        return modules

    def list_names(self) -> list[str]:
        return [entry.name for entry in self.discover()]
