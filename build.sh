#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHISO_DIR="$PROJECT_ROOT/archiso"
EXTRA_PACKAGES_FILE="$PROJECT_ROOT/packages/zentrix-extra.x86_64"
STAGING_ROOT="$PROJECT_ROOT/.d"
STAGING_PROFILE="$STAGING_ROOT/profile"
WORK_DIR="$PROJECT_ROOT/work"
OUT_DIR="$PROJECT_ROOT/out"
RESOLVED_EXTRA_PACKAGES_FILE="$STAGING_ROOT/packages-resolved.x86_64"
BOOT_BRANDING_SCRIPT="$PROJECT_ROOT/scripts/brand-boot-menu.sh"
ASSET_SYNC_SCRIPT="$PROJECT_ROOT/scripts/sync-live-assets.sh"
ISO_FINAL_NAME="zentrix-by-abraham-tobal-1.0-x86_64.iso"
BASE_PROFILE=""
LOCAL_REPO_PATH="${ZENTRIX_LOCAL_REPO:-}"
CALAMARES_PACKAGE_GLOB="calamares-*.pkg.tar.zst"
ZENTRIX_PLATFORM_DIR="$PROJECT_ROOT/zentrix-platform"

log() {
  printf '[d] %s\n' "$*"
}

fail() {
  printf '[d][error] %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "No se encontro el comando requerido: $1"
}

detect_base_profile() {
  local candidates=(
    "/usr/share/archiso/configs/releng"
    "/usr/share/archiso/configs/baseline"
    "/usr/share/archiso/configs/default"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -d "$candidate" && -f "$candidate/packages.x86_64" ]]; then
      BASE_PROFILE="$candidate"
      return 0
    fi
  done

  fail "No se encontro un perfil base de Archiso. Instala archiso (sudo pacman -S archiso)."
}

check_host() {
  if [[ "$(uname -s)" != "Linux" ]]; then
    fail "Este script solo puede ejecutarse en Linux."
  fi

  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    if [[ "${ID:-}" != "arch" && "${ID_LIKE:-}" != *"arch"* ]]; then
      log "Advertencia: host no identificado como Arch. Se intentara continuar."
    fi
  fi
}

check_dependencies() {
  require_command mkarchiso
  require_command rsync
  require_command awk
  require_command sort
  require_command sed

  [[ -x "$BOOT_BRANDING_SCRIPT" ]] || fail "No existe o no es ejecutable: $BOOT_BRANDING_SCRIPT"
  [[ -x "$ASSET_SYNC_SCRIPT" ]] || fail "No existe o no es ejecutable: $ASSET_SYNC_SCRIPT"
}

prepare_dirs() {
  mkdir -p "$STAGING_ROOT" "$WORK_DIR" "$OUT_DIR"
  rm -rf "$STAGING_PROFILE"
  rm -f "$RESOLVED_EXTRA_PACKAGES_FILE"
  mkdir -p "$STAGING_PROFILE"
}

stage_profile() {
  [[ -d "$BASE_PROFILE" ]] || fail "No existe el perfil base de archiso en $BASE_PROFILE"
  [[ -d "$ARCHISO_DIR" ]] || fail "No existe el directorio archiso del proyecto"

  log "Copiando perfil base releng..."
  rsync -a --delete "$BASE_PROFILE/" "$STAGING_PROFILE/"

  log "Aplicando overrides del proyecto..."
  rsync -a "$ARCHISO_DIR/" "$STAGING_PROFILE/"
}

configure_optional_local_repo() {
  if [[ -z "$LOCAL_REPO_PATH" ]]; then
    fail "Define ZENTRIX_LOCAL_REPO con un repo local que contenga $CALAMARES_PACKAGE_GLOB para construir una ISO instalable."
  fi

  [[ -d "$LOCAL_REPO_PATH" ]] || fail "ZENTRIX_LOCAL_REPO apunta a un directorio inexistente: $LOCAL_REPO_PATH"
  compgen -G "$LOCAL_REPO_PATH/$CALAMARES_PACKAGE_GLOB" >/dev/null || fail "No se encontro $LOCAL_REPO_PATH/$CALAMARES_PACKAGE_GLOB"

  log "Agregando repo local opcional: $LOCAL_REPO_PATH"
  cat >> "$STAGING_PROFILE/pacman.conf" <<EOF

[zentrix-local]
SigLevel = Optional TrustAll
Server = file://$LOCAL_REPO_PATH
EOF
}

package_exists() {
  local package_name="$1"

  # Calamares viene del repositorio local de Zentrix
  if [[ "$package_name" == "calamares" && -n "$LOCAL_REPO_PATH" ]]; then
    if compgen -G "$LOCAL_REPO_PATH/calamares-*.pkg.tar.zst" >/dev/null; then
      return 0
    fi
  fi

  pacman --config "$STAGING_PROFILE/pacman.conf" -Si "$package_name" >/dev/null 2>&1
}

resolve_package_name() {
  local package_name="$1"

  if [[ "$package_name" == "python-pyside6" ]]; then
    if package_exists "pyside6"; then
      log "Reemplazando paquete no valido: python-pyside6 -> pyside6"
      printf '%s\n' "pyside6"
      return 0
    fi
  fi

  if package_exists "$package_name"; then
    printf '%s\n' "$package_name"
    return 0
  fi

  if [[ "$package_name" == "calamares" ]]; then
    fail "El paquete 'calamares' no esta disponible en los repos configurados. Verifica tu repo local en ZENTRIX_LOCAL_REPO."
  fi

  fail "El paquete '$package_name' no existe en los repos configurados para Archiso."
}

resolve_extra_packages() {
  [[ -f "$EXTRA_PACKAGES_FILE" ]] || fail "No existe $EXTRA_PACKAGES_FILE"

  : > "$RESOLVED_EXTRA_PACKAGES_FILE"

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ -z "$line" || "$line" == \#* ]]; then
      continue
    fi

    local resolved_name
    resolved_name="$(resolve_package_name "$line")"
    if [[ -n "$resolved_name" ]]; then
      printf '%s\n' "$resolved_name" >> "$RESOLVED_EXTRA_PACKAGES_FILE"
    fi
  done < "$EXTRA_PACKAGES_FILE"
}

merge_packages() {
  log "Fusionando paquetes base + Zentrix..."
  resolve_extra_packages
  awk '!seen[$0]++' \
    "$BASE_PROFILE/packages.x86_64" \
    "$RESOLVED_EXTRA_PACKAGES_FILE" \
    > "$STAGING_PROFILE/packages.x86_64"
}

sync_live_assets() {
  log "Sincronizando logos y wallpapers al perfil de d..."
  "$ASSET_SYNC_SCRIPT" "$PROJECT_ROOT" "$STAGING_PROFILE"
}

brand_boot_menu() {
  log "Aplicando branding de arranque (Fase 3)..."
  "$BOOT_BRANDING_SCRIPT" "$STAGING_PROFILE"
}

stage_zentrix_platform() {
  [[ -d "$ZENTRIX_PLATFORM_DIR" ]] || fail "No existe el directorio de la plataforma: $ZENTRIX_PLATFORM_DIR"

  log "Integrando Zentrix Platform en el rootfs instalable..."

  install -d "$STAGING_PROFILE/airootfs/usr/share/zentrix-platform"
  rsync -a --delete \
    --exclude '.git/' \
    --exclude '.pytest_cache/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.venv/' \
    --exclude '.runtime/' \
    "$ZENTRIX_PLATFORM_DIR/" \
    "$STAGING_PROFILE/airootfs/usr/share/zentrix-platform/"

  install -d "$STAGING_PROFILE/airootfs/usr/lib/systemd/system"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/systemd/zentrix-core.service" "$STAGING_PROFILE/airootfs/usr/lib/systemd/system/"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/systemd/zentrix-core.path" "$STAGING_PROFILE/airootfs/usr/lib/systemd/system/"

  install -d "$STAGING_PROFILE/airootfs/usr/lib/tmpfiles.d"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/systemd/tmpfiles.d/zentrix-core.conf" "$STAGING_PROFILE/airootfs/usr/lib/tmpfiles.d/"

  install -d "$STAGING_PROFILE/airootfs/etc/zentrix"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/packaging/etc/zentrix/zentrix.yaml" "$STAGING_PROFILE/airootfs/etc/zentrix/"

  install -d "$STAGING_PROFILE/airootfs/usr/share/dbus-1/system-services"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/packaging/dbus-1/system-services/org.zentrix.Core.service" "$STAGING_PROFILE/airootfs/usr/share/dbus-1/system-services/"

  install -d "$STAGING_PROFILE/airootfs/etc/dbus-1/system.d"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/packaging/dbus-1/system.d/org.zentrix.Core.conf" "$STAGING_PROFILE/airootfs/etc/dbus-1/system.d/"

  install -d "$STAGING_PROFILE/airootfs/usr/share/polkit-1/actions"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/polkit/org.zentrix.core.policy" "$STAGING_PROFILE/airootfs/usr/share/polkit-1/actions/"

  install -d "$STAGING_PROFILE/airootfs/usr/share/applications"
  install -m 0644 "$ZENTRIX_PLATFORM_DIR/packaging/applications/zentrix-control-center.desktop" "$STAGING_PROFILE/airootfs/usr/share/applications/"
}

run_mkarchiso() {
  log "Iniciando compilacion de ISO..."
  sudo mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$STAGING_PROFILE"
}

finalize_iso_name() {
  local latest_iso
  latest_iso="$(find "$OUT_DIR" -maxdepth 1 -type f -name '*.iso' -printf '%T@ %p\n' | sort -nr | awk 'NR==1{print $2}')"

  [[ -n "${latest_iso:-}" ]] || fail "No se encontro ningun archivo ISO tras la compilacion."

  local target_iso="$OUT_DIR/$ISO_FINAL_NAME"
  if [[ "$latest_iso" != "$target_iso" ]]; then
    cp -f "$latest_iso" "$target_iso"
    log "ISO final preparada: $target_iso"
  else
    log "ISO final ya tiene el nombre esperado: $target_iso"
  fi
}

main() {
  log "Validando entorno..."
  check_host
  check_dependencies
  detect_base_profile
  log "Perfil base detectado: $BASE_PROFILE"
  prepare_dirs
  stage_profile
  configure_optional_local_repo
  merge_packages
  stage_zentrix_platform
  sync_live_assets
  brand_boot_menu
  run_mkarchiso
  finalize_iso_name

  log "Compilacion finalizada. Revisa la carpeta: $OUT_DIR"
}

main "$@"
