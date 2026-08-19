from __future__ import annotations

from dataclasses import asdict
from typing import Any

from core.models import ActionPlan, OperationResult


class ModuleBase:
    name = "base"
    description = "Base module"

    def info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }

    def plan(self, profile: dict[str, Any]) -> list[ActionPlan]:
        return [
            ActionPlan(
                name=f"{self.name}.noop",
                description="No-op baseline action",
            )
        ]

    def apply(self, profile: dict[str, Any], dry_run: bool = True) -> OperationResult:
        plans = [asdict(p) for p in self.plan(profile)]
        msg = "Planned actions only" if dry_run else "Applied safely"
        return OperationResult(ok=True, message=msg, data={"plans": plans})
