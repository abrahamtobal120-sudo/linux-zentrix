from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionPlan:
    name: str
    description: str
    commands: list[str] = field(default_factory=list)
    requires_reboot: bool = False


@dataclass
class OperationResult:
    ok: bool
    message: str
    changes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
