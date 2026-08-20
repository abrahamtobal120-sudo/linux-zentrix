from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class ParentalModule(ModuleBase):
    name = "parental"
    description = "Zentrix parental module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"parental.plan",
                description=f"Prepare parental settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
