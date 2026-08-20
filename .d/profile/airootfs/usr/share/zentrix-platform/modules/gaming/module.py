from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class GamingModule(ModuleBase):
    name = "gaming"
    description = "Zentrix gaming module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"gaming.plan",
                description=f"Prepare gaming settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
