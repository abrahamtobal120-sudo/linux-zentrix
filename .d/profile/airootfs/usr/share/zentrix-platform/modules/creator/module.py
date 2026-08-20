from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class CreatorModule(ModuleBase):
    name = "creator"
    description = "Zentrix creator module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"creator.plan",
                description=f"Prepare creator settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
