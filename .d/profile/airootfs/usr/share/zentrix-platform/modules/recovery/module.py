from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class RecoveryModule(ModuleBase):
    name = "recovery"
    description = "Zentrix recovery module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"recovery.plan",
                description=f"Prepare recovery settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
