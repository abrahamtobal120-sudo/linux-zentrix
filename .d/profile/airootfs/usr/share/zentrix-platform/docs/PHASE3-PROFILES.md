# Phase 3 - Zentrix Profiles Engine

This phase upgrades profiles from static labels into a reversible engine.

## Implemented

- Previous profile snapshot storage in Core state
- Restore-previous-profile support in daemon API
- Profile diff generation between current and target profile
- History exposure through D-Bus API
- `zentrix-mode restore`
- `zentrix-mode history`
- Control Center profile preview, apply, restore, and history view

## Safety model

- Preview uses dry-run path
- Apply stores previous profile before switching
- Restore uses the same controlled module flow
- No hidden destructive operations

## Next step

The next phase should bind real updater and snapshot logic so profile changes can optionally create system restore points.
