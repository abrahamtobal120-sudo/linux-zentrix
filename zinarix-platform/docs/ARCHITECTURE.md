# Zinarix Platform Architecture

## Layering

1. GUI applications
2. API client (D-Bus)
3. Zinarix daemon (privileged core)
4. System operations through controlled modules

## Why this matters

- GUI is not root.
- Sensitive operations are centralized and auditable.
- Profiles and modules are reversible and data-driven.
- New modes can be added through YAML and module updates.

## IPC and security

- IPC is provided through D-Bus: org.zinarix.Core
- systemd unit runs privileged daemon
- Polkit policy gates privileged actions

## First implemented commands

- zinarixctl
- zinarix-mode
- zinarix-health
- zinarix-drivers
- zinarix-repair
- zinarix-security
- zinarix-app
- zinarix-snapshot
- zinarix-firewall

This is phase 1. Feature logic is intentionally conservative and safe by default.
