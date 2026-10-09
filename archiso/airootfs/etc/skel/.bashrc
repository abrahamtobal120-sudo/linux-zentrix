# ~/.bashrc for Zinarix live user

if [[ -n "${PS1:-}" ]] && command -v zinarix-welcome >/dev/null 2>&1; then
  # Optional welcome banner in interactive terminals.
  if [[ "${ZINARIX_WELCOME_DISABLED:-0}" != "1" ]]; then
    marker="/tmp/zinarix-welcome-shown-${UID}"
    if [[ "${ZINARIX_WELCOME_ALWAYS:-0}" == "1" || ! -f "$marker" ]]; then
      zinarix-welcome
      : > "$marker"
    fi
  fi
fi
