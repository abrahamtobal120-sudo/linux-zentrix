from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CoreState:
    current_profile: str = "normal"
    active_mode: str = "normal"
    last_update_check: str = ""
    previous_profile: str = ""
    previous_mode: str = ""
    pending_restore: dict[str, Any] = field(default_factory=dict)
    module_state: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)


class StateStore:
    def __init__(self, state_file: str) -> None:
        self.state_path = Path(state_file)

    def load(self) -> CoreState:
        if not self.state_path.exists():
            return CoreState()

        raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        return CoreState(
            current_profile=raw.get("current_profile", "normal"),
            active_mode=raw.get("active_mode", "normal"),
            last_update_check=raw.get("last_update_check", ""),
            previous_profile=raw.get("previous_profile", ""),
            previous_mode=raw.get("previous_mode", ""),
            pending_restore=raw.get("pending_restore", {}),
            module_state=raw.get("module_state", {}),
            history=raw.get("history", []),
        )

    def save(self, state: CoreState) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_profile": state.current_profile,
            "active_mode": state.active_mode,
            "last_update_check": state.last_update_check,
            "previous_profile": state.previous_profile,
            "previous_mode": state.previous_mode,
            "pending_restore": state.pending_restore,
            "module_state": state.module_state,
            "history": state.history,
        }
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(self.state_path)

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
