#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Uso: $0 <staging-profile-dir>" >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGING_PROFILE="$1"
CUSTOM_SPLASH="$PROJECT_ROOT/archiso/syslinux/splash.png"

if [[ ! -d "$STAGING_PROFILE" ]]; then
  echo "[brand-boot-menu][error] No existe directorio: $STAGING_PROFILE" >&2
  exit 1
fi

log() {
  printf '[brand-boot-menu] %s\n' "$*"
}

install_syslinux_splash() {
  local dest_dir="$STAGING_PROFILE/syslinux"
  local head_cfg="$dest_dir/archiso_head.cfg"

  [[ -s "$CUSTOM_SPLASH" ]] || {
    echo "[brand-boot-menu][error] Falta el splash Zentrix: $CUSTOM_SPLASH" >&2
    exit 1
  }

  mkdir -p "$dest_dir"
  install -m 0644 "$CUSTOM_SPLASH" "$dest_dir/splash.png"
  log "Splash BIOS Zentrix instalado: $dest_dir/splash.png"

  if [[ -f "$head_cfg" ]]; then
    if grep -q '^MENU BACKGROUND ' "$head_cfg"; then
      sed -i 's|^MENU BACKGROUND .*|MENU BACKGROUND splash.png|' "$head_cfg"
    else
      printf '\nMENU BACKGROUND splash.png\n' >> "$head_cfg"
    fi
  fi
}

patch_file_if_exists() {
  local file="$1"

  if [[ -f "$file" ]]; then
    log "Actualizando: $file"

    case "$file" in
      *.cfg)
        sed -i \
          -e 's/^MENU TITLE .*/MENU TITLE ZENTRIX/' \
          -e 's/Boot Arch Linux (x86_64)/Zentrix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, BIOS) with \^speech/Zentrix Live with ^speech/g' \
          -e 's/Arch Linux install medium (%ARCH%, BIOS)/Zentrix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, NBD)/Zentrix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, NFS)/Zentrix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, HTTP)/Zentrix Live/g' \
          -e 's/Arch Linux install medium (x86_64, UEFI)/Zentrix Live/g' \
          -e 's/Arch Linux install medium (x86_64)/Zentrix Live/g' \
          "$file"
        ;;
    esac
  fi
}

patch_all_syslinux_configs() {
  local dir="$STAGING_PROFILE/syslinux"
  [[ -d "$dir" ]] || return 0

  local file
  for file in "$dir"/*.cfg; do
    [[ -f "$file" ]] || continue
    patch_file_if_exists "$file"
  done
}

patch_systemd_boot_entries() {
  local dir="$1"

  [[ -d "$dir" ]] || return 0

  local f

  for f in "$dir"/*.conf; do
    [[ -f "$f" ]] || continue

    log "Ajustando entrada UEFI: $f"

    if grep -qi 'zentrix_install=1' "$f"; then
      sed -i -E 's/^title.*/title    Install Zentrix/' "$f"
    elif grep -qi 'zentrix_guest=1' "$f"; then
      sed -i -E 's/^title.*/title    Zentrix Guest Mode/' "$f"
    elif grep -qi 'accessibility=on' "$f"; then
      sed -i -E 's/^title.*/title    Zentrix Live with speech/' "$f"
    elif grep -qi 'memtest' "$f"; then
      sed -i -E 's/^title.*/title    Advanced options/' "$f"
    else
      sed -i -E 's/^title.*/title    Zentrix Live/' "$f"
    fi
  done
}

verify_visible_branding() {
  local bad=0

  if [[ ! -s "$STAGING_PROFILE/syslinux/splash.png" ]]; then
    echo "[brand-boot-menu][error] No quedó instalado el splash BIOS de Zentrix" >&2
    bad=1
  fi

  if grep -RniE 'MENU (TITLE|LABEL).*Arch Linux|Boot Arch Linux|Arch Linux install medium' "$STAGING_PROFILE/syslinux" --include='*.cfg' 2>/dev/null; then
    echo "[brand-boot-menu][error] Quedó texto visible de Arch Linux en el menú BIOS" >&2
    bad=1
  fi

  if [[ "$bad" -ne 0 ]]; then
    exit 1
  fi

  log "Branding visible verificado: ZENTRIX"
}

main() {
  log "Aplicando branding de menu de arranque"

  # BIOS / Syslinux: fuerza el splash propio y elimina etiquetas visibles de Arch.
  install_syslinux_splash
  patch_all_syslinux_configs

  # UEFI / systemd-boot
  patch_systemd_boot_entries "$STAGING_PROFILE/efiboot/loader/entries"

  verify_visible_branding
  log "Branding de boot aplicado"
}

main "$@"
