from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class SnapshotsModule(ModuleBase):
    name = "snapshots"
    description = "Zentrix snapshots module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"snapshots.plan",
                description=f"Prepare snapshots settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
