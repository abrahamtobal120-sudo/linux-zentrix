from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class DeveloperModule(ModuleBase):
    name = "developer"
    description = "Zentrix developer module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"developer.plan",
                description=f"Prepare developer settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
