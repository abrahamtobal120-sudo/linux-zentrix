#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Uso: $0 <project-root> <staging-profile-dir>" >&2
  exit 1
fi

PROJECT_ROOT="$1"
STAGING_PROFILE="$2"

SRC_LOGOS_DIR="$PROJECT_ROOT/assets/logos"
SRC_WALLPAPERS_DIR="$PROJECT_ROOT/assets/wallpapers"
DEST_ROOT="$STAGING_PROFILE/airootfs/usr/share/zentrix"
DEST_LOGOS_DIR="$DEST_ROOT/logos"
DEST_WALLPAPERS_DIR="$DEST_ROOT/wallpapers"
DEST_SYSTEM_WALLPAPER_DIR="$STAGING_PROFILE/airootfs/usr/share/wallpapers"
DEST_PLYMOUTH_THEME_DIR="$STAGING_PROFILE/airootfs/usr/share/plymouth/themes/zentrix"
DEST_GRUB_THEME_DIR="$STAGING_PROFILE/airootfs/usr/share/grub/themes/zentrix"

require_file() {
  [[ -f "$1" ]] || {
    echo "[sync-live-assets][error] Falta archivo: $1" >&2
    exit 1
  }
}

require_file "$SRC_LOGOS_DIR/zentrix-logo-master.png"
require_file "$SRC_WALLPAPERS_DIR/zentrix-dark-1920x1080.png"

mkdir -p "$DEST_LOGOS_DIR" "$DEST_WALLPAPERS_DIR" "$DEST_SYSTEM_WALLPAPER_DIR"
mkdir -p "$DEST_PLYMOUTH_THEME_DIR" "$DEST_GRUB_THEME_DIR"

cp "$SRC_LOGOS_DIR/zentrix-logo-master.png" "$DEST_LOGOS_DIR/zentrix-logo-master.png"
cp "$SRC_LOGOS_DIR/zentrix-main-logo.png" "$DEST_LOGOS_DIR/zentrix-main-logo.png"
cp "$SRC_LOGOS_DIR/zentrix-menu-logo.png" "$DEST_LOGOS_DIR/zentrix-menu-logo.png"
cp "$SRC_LOGOS_DIR/zentrix-sddm-logo.png" "$DEST_LOGOS_DIR/zentrix-sddm-logo.png"
cp "$SRC_LOGOS_DIR/zentrix-plymouth-logo.png" "$DEST_LOGOS_DIR/zentrix-plymouth-logo.png"
cp "$SRC_LOGOS_DIR/zentrix-grub-logo.png" "$DEST_LOGOS_DIR/zentrix-grub-logo.png"
cp "$SRC_LOGOS_DIR/zentrix-fastfetch-logo.png" "$DEST_LOGOS_DIR/zentrix-fastfetch-logo.png"

cp "$SRC_WALLPAPERS_DIR/zentrix-dark-1920x1080.png" "$DEST_WALLPAPERS_DIR/zentrix-dark-1920x1080.png"
cp "$SRC_WALLPAPERS_DIR/zentrix-dark-2560x1440.png" "$DEST_WALLPAPERS_DIR/zentrix-dark-2560x1440.png"
cp "$SRC_WALLPAPERS_DIR/zentrix-dark-4k.png" "$DEST_WALLPAPERS_DIR/zentrix-dark-4k.png"

# System-wide default wallpaper used by first-run KDE script.
cp "$SRC_WALLPAPERS_DIR/zentrix-dark-1920x1080.png" "$DEST_SYSTEM_WALLPAPER_DIR/zentrix-dark.png"

# Boot branding assets.
cp "$SRC_LOGOS_DIR/zentrix-plymouth-logo.png" "$DEST_PLYMOUTH_THEME_DIR/logo.png"
cp "$SRC_LOGOS_DIR/zentrix-grub-logo.png" "$DEST_GRUB_THEME_DIR/logo.png"
cp "$SRC_WALLPAPERS_DIR/zentrix-dark-1920x1080.png" "$DEST_GRUB_THEME_DIR/background.png"

echo "[sync-live-assets] Assets sincronizados en perfil de build"
