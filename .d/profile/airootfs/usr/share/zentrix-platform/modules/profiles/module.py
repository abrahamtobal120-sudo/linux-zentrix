from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class ProfilesModule(ModuleBase):
    name = "profiles"
    description = "Zentrix profiles module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"profiles.plan",
                description=f"Prepare profiles settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
