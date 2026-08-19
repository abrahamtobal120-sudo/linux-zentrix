from __future__ import annotations

from modules.base import ModuleBase
from modules.creator.module import CreatorModule
from modules.developer.module import DeveloperModule
from modules.drivers.module import DriversModule
from modules.firewall.module import FirewallModule
from modules.gaming.module import GamingModule
from modules.parental.module import ParentalModule
from modules.privacy.module import PrivacyModule
from modules.profiles.module import ProfilesModule
from modules.recovery.module import RecoveryModule
from modules.security.module import SecurityModule
from modules.snapshots.module import SnapshotsModule
from modules.updater.module import UpdaterModule


def default_modules() -> dict[str, ModuleBase]:
    entries = [
        UpdaterModule(),
        DriversModule(),
        ProfilesModule(),
        ParentalModule(),
        CreatorModule(),
        DeveloperModule(),
        SecurityModule(),
        GamingModule(),
        RecoveryModule(),
        SnapshotsModule(),
        PrivacyModule(),
        FirewallModule(),
    ]
    return {m.name: m for m in entries}
