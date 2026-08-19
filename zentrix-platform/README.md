# Zentrix Platform

Zentrix Platform is the service layer that makes Zentrix feel like its own OS,
while Arch Linux remains the technical base.

## Scope of this phase

This phase implements the platform architecture and working core services:

- Zentrix Core configuration and state management
- Privileged daemon over D-Bus
- API client layer
- CLI base commands
- Modular plugin registry
- Profile definitions in YAML
- Polkit policy and systemd service definitions

Current GUI phase status:

- Phase 2 base Control Center implemented in `gui/control_center.py`
- Desktop launcher included in `packaging/applications/zentrix-control-center.desktop`
- Phase 3 profiles engine implemented with preview, restore, and history support

## Run locally (development)

```bash
cd zentrix-platform
python -m venv .venv
source .venv/bin/activate
pip install -e .
python daemon/main.py --bus session
```

In another shell:

```bash
zentrixctl ping --bus session
zentrixctl status --bus session
zentrixctl profile list --bus session
zentrix-mode status --bus session
```

## Service model

GUI -> API client -> D-Bus daemon -> controlled system operations

No GUI tool should run as root directly.
