#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGO_DIR="$PROJECT_ROOT/assets/logos"
MASTER="$LOGO_DIR/zinarix-logo-master.png"

if [[ ! -f "$MASTER" ]]; then
  echo "[sync-brand-assets][error] No existe: $MASTER" >&2
  exit 1
fi

targets=(
  "zinarix-main-logo.png"
  "zinarix-menu-logo.png"
  "zinarix-sddm-logo.png"
  "zinarix-plymouth-logo.png"
  "zinarix-grub-logo.png"
  "zinarix-fastfetch-logo.png"
)

for target in "${targets[@]}"; do
  cp "$MASTER" "$LOGO_DIR/$target"
  echo "[sync-brand-assets] actualizado: $target"
done

echo "[sync-brand-assets] completado"
