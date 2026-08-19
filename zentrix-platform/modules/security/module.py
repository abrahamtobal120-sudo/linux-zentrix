from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class SecurityModule(ModuleBase):
    name = "security"
    description = "Zentrix security module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"security.plan",
                description=f"Prepare security settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
