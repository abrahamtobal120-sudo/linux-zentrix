# Zentrix Core Configuration

Default file path:

- /etc/zentrix/zentrix.yaml

Example:

```yaml
name: Zentrix
version: "1.0"
telemetry_enabled: false
log_file: /var/log/zentrix/core.log
state_file: /var/lib/zentrix/state.json
profile_dir: /usr/share/zentrix-platform/profiles
module_allowlist: []
```

Telemetry is OFF by default.
