# Zentrix Platform Architecture

## Layering

1. GUI applications
2. API client (D-Bus)
3. Zentrix daemon (privileged core)
4. System operations through controlled modules

## Why this matters

- GUI is not root.
- Sensitive operations are centralized and auditable.
- Profiles and modules are reversible and data-driven.
- New modes can be added through YAML and module updates.

## IPC and security

- IPC is provided through D-Bus: org.zentrix.Core
- systemd unit runs privileged daemon
- Polkit policy gates privileged actions

## First implemented commands

- zentrixctl
- zentrix-mode
- zentrix-health
- zentrix-drivers
- zentrix-repair
- zentrix-security
- zentrix-app
- zentrix-snapshot
- zentrix-firewall

This is phase 1. Feature logic is intentionally conservative and safe by default.
