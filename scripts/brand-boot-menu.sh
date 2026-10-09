#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Uso: $0 <staging-profile-dir>" >&2
  exit 1
fi

STAGING_PROFILE="$1"

if [[ ! -d "$STAGING_PROFILE" ]]; then
  echo "[brand-boot-menu][error] No existe directorio: $STAGING_PROFILE" >&2
  exit 1
fi

log() {
  printf '[brand-boot-menu] %s\n' "$*"
}

patch_file_if_exists() {
  local file="$1"

  if [[ -f "$file" ]]; then
    log "Actualizando: $file"

    case "$file" in
      *.cfg)
        sed -i \
          -e 's/^MENU TITLE .*/MENU TITLE ZINARIX/' \
          -e 's/Boot Arch Linux (x86_64)/Zinarix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, BIOS) with \^speech/Zinarix Live with ^speech/g' \
          -e 's/Arch Linux install medium (%ARCH%, BIOS)/Zinarix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, NBD)/Zinarix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, NFS)/Zinarix Live/g' \
          -e 's/Arch Linux install medium (%ARCH%, HTTP)/Zinarix Live/g' \
          -e 's/Arch Linux install medium (x86_64, UEFI)/Zinarix Live/g' \
          -e 's/Arch Linux install medium (x86_64)/Zinarix Live/g' \
          "$file"
        ;;
    esac
  fi
}

patch_systemd_boot_entries() {
  local dir="$1"

  [[ -d "$dir" ]] || return 0

  local f

  for f in "$dir"/*.conf; do
    [[ -f "$f" ]] || continue

    log "Ajustando entrada UEFI: $f"

    if grep -qi 'zinarix_install=1' "$f"; then
      sed -i -E 's/^title.*/title    Install Zinarix/' "$f"

    elif grep -qi 'zinarix_guest=1' "$f"; then
      sed -i -E 's/^title.*/title    Zinarix Guest Mode/' "$f"

    elif grep -qi 'accessibility=on' "$f"; then
      sed -i -E 's/^title.*/title    Zinarix Live with speech/' "$f"

    elif grep -qi 'memtest' "$f"; then
      sed -i -E 's/^title.*/title    Advanced options/' "$f"

    else
      sed -i -E 's/^title.*/title    Zinarix Live/' "$f"
    fi
  done
}

main() {
  log "Aplicando branding de menu de arranque"

  # BIOS / Syslinux
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_sys-linux.cfg"
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_head.cfg"
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_pxe-linux.cfg"
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_pxe.cfg"

  # UEFI / systemd-boot
  patch_systemd_boot_entries "$STAGING_PROFILE/efiboot/loader/entries"

  log "Branding de boot aplicado"
}

main "$@"
