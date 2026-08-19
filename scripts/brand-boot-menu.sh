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
    sed -i \
      -e 's/Boot Arch Linux (x86_64)/Try Zentrix/g' \
      -e 's/Arch Linux install medium (x86_64, UEFI)/Try Zentrix/g' \
      -e 's/MENU TITLE.*/MENU TITLE ZENTRIX/g' \
      -e 's/Boot existing OS/Advanced options/g' \
      -e 's/UEFI Shell/Advanced options/g' \
      "$file"
  fi
}

patch_systemd_boot_entries() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0

  local f
  for f in "$dir"/*.conf; do
    [[ -f "$f" ]] || continue

    log "Ajustando entrada UEFI: $f"
    if grep -qi 'fallback\|memtest\|hardware\|uefi shell' "$f"; then
      sed -i -E 's/^title.*/title   Advanced options/' "$f"
    else
      sed -i -E 's/^title.*/title   Try Zentrix/' "$f"
    fi
  done
}

main() {
  log "Aplicando branding de menu de arranque"

  # Common syslinux locations in archiso profiles.
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_sys-linux.cfg"
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_head.cfg"
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_pxe-linux.cfg"
  patch_file_if_exists "$STAGING_PROFILE/syslinux/archiso_pxe.cfg"

  # Common systemd-boot location in archiso profiles.
  patch_systemd_boot_entries "$STAGING_PROFILE/efiboot/loader/entries"

  log "Branding de boot aplicado"
}

main "$@"
