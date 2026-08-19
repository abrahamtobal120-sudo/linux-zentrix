from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class UpdaterModule(ModuleBase):
    name = "updater"
    description = "Zentrix updater module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"updater.plan",
                description=f"Prepare updater settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
