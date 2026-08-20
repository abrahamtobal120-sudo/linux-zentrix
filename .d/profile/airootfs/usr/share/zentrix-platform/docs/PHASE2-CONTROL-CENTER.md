# Phase 2 - Zentrix Control Center

This phase introduces the first real GUI on top of Zentrix Core.

## Implemented

- Base desktop app: Zentrix Control Center
- D-Bus backed status dashboard
- Profile listing and dry-run/apply workflow
- Update actions panel
- Driver actions panel
- About page explaining privilege model

## Safety model

- GUI does not run as root
- Profile changes go through Zentrix Core
- Dry-run is available before applying changes

## Current scope

This is the base shell for the future full Control Center. It focuses on:

- Dashboard
- Profiles
- Updates entry points
- Drivers entry points

Later phases will fill in:

- privacy
- firewall
- parental control
- snapshots
- recovery
- users
- battery
- Bluetooth
- storage