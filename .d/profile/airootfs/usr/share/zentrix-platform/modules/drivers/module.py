from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class DriversModule(ModuleBase):
    name = "drivers"
    description = "Zentrix drivers module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"drivers.plan",
                description=f"Prepare drivers settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
