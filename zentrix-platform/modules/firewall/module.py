from __future__ import annotations

from modules.base import ModuleBase
from core.models import ActionPlan


class FirewallModule(ModuleBase):
    name = "firewall"
    description = "Zentrix firewall module"

    def plan(self, profile: dict[str, object]) -> list[ActionPlan]:
        profile_name = str(profile.get("name", "custom"))
        return [
            ActionPlan(
                name=f"firewall.plan",
                description=f"Prepare firewall settings for profile: {profile_name}",
                commands=[],
                requires_reboot=False,
            )
        ]
