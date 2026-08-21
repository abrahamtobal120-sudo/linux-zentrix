from __future__ import annotations

from core.parental import ParentalAgent
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

    def apply(self, profile: dict[str, object], dry_run: bool = True):
        result = super().apply(profile, dry_run=dry_run)
        if not dry_run:
            agent = ParentalAgent()
            policy_users = list(profile.get("parental_users", [])) if isinstance(profile, dict) else []
            if policy_users:
                agent.apply_demo_policy(policy_users)
        return result
