#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[customize_airootfs] %s\n' "$*"
}

enable_if_present() {
  local unit="$1"
  if [[ -f "/usr/lib/systemd/system/$unit" ]]; then
    log "Habilitando servicio: $unit"
    systemctl enable "$unit"
  else
    log "Servicio no disponible, se omite: $unit"
  fi
}

disable_if_present() {
  local unit="$1"
  if [[ -f "/usr/lib/systemd/system/$unit" ]]; then
    log "Deshabilitando servicio: $unit"
    systemctl disable "$unit" || true
  fi
}

configure_live_user() {
  local user="zentrix"

  if ! id -u "$user" >/dev/null 2>&1; then
    log "Creando usuario live: $user"
    useradd -m -G wheel,audio,video,storage,optical -s /bin/bash "$user"
  fi

  install -d -m 0755 -o "$user" -g "$user" "/home/$user/Desktop"
  install -d -m 0755 -o "$user" -g "$user" "/home/$user/.config/autostart"

  # Do not hardcode passwords; live login is handled by SDDM autologin.
  passwd -l "$user" >/dev/null 2>&1 || true

  cat > "/home/$user/.bash_profile" <<'EOT'
# Auto-start KDE Plasma only for the temporary live user on tty1.
if [[ -z "${DISPLAY:-}" && "$(tty)" == "/dev/tty1" ]]; then
  if command -v startplasma-x11 >/dev/null 2>&1; then
    exec dbus-run-session startplasma-x11
  elif command -v startx >/dev/null 2>&1; then
    exec startx
  fi
fi
EOT
  chown "$user:$user" "/home/$user/.bash_profile"

  cat > "/home/$user/.config/autostart/zentrix-live-start.desktop" <<'EOT'
[Desktop Entry]
Type=Application
Name=Zentrix Live Start
Comment=Choose between trying and installing Zentrix
Exec=/usr/local/bin/zentrix-live-start
OnlyShowIn=KDE;
X-KDE-autostart-phase=2
X-KDE-StartupNotify=false
NoDisplay=true
EOT
  chown "$user:$user" "/home/$user/.config/autostart/zentrix-live-start.desktop"

  cat > "/home/$user/Desktop/Install Zentrix.desktop" <<'EOT'
[Desktop Entry]
Type=Application
Name=Install Zentrix
Comment=Install Zentrix by Abraham Tobal
Exec=zentrix-install
Icon=drive-harddisk
Terminal=false
Categories=System;
StartupNotify=true
EOT
  chown "$user:$user" "/home/$user/Desktop/Install Zentrix.desktop"
  chmod 0755 "/home/$user/Desktop/Install Zentrix.desktop"
}

configure_identity() {
  log "Aplicando identidad Zentrix"
  cat > /etc/issue <<'EOT'
ZENTRIX by Abraham Tobal
EOT
}

configure_sddm() {
  log "Configurando SDDM para sesion live"

  install -d -m 0755 /etc/sddm.conf.d
  cat > /etc/sddm.conf.d/zentrix-live.conf <<'EOT'
[Autologin]
User=zentrix
Session=plasma.desktop

[General]
DisplayServer=x11

[Theme]
Current=zentrix
EOT

  enable_if_present "sddm.service"

  # Prevent conflicts with getty on tty1 when display manager is active.
  disable_if_present "getty@tty1.service"
}

configure_plymouth() {
  log "Configurando Plymouth"
  if command -v plymouth-set-default-theme >/dev/null 2>&1; then
    plymouth-set-default-theme -R zentrix || true
  else
    log "plymouth-set-default-theme no disponible, se omite"
  fi
}

main() {
  configure_identity
  configure_live_user

  # Enable only essential services if corresponding packages are in the image.
  enable_if_present "NetworkManager.service"
  enable_if_present "bluetooth.service"
  enable_if_present "zentrix-core.service"
  enable_if_present "zentrix-core.path"
  configure_sddm
  configure_plymouth

  log "Personalizacion de airootfs completada"
}

main "$@"
