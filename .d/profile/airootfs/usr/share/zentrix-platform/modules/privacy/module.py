from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class PrivacyModule(ModuleBase):
    name = "privacy"
    description = "Zentrix privacy module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"privacy.plan",
                description=f"Prepare privacy settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
