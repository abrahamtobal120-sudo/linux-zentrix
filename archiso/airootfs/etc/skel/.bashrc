# ~/.bashrc for Zentrix live user

if [[ -n "${PS1:-}" ]] && command -v zentrix-welcome >/dev/null 2>&1; then
  # Optional welcome banner in interactive terminals.
  if [[ "${ZENTRIX_WELCOME_DISABLED:-0}" != "1" ]]; then
    marker="/tmp/zentrix-welcome-shown-${UID}"
    if [[ "${ZENTRIX_WELCOME_ALWAYS:-0}" == "1" || ! -f "$marker" ]]; then
      zentrix-welcome
      : > "$marker"
    fi
  fi
fi
