#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGO_DIR="$PROJECT_ROOT/assets/logos"
MASTER="$LOGO_DIR/zentrix-logo-master.png"

if [[ ! -f "$MASTER" ]]; then
  echo "[sync-brand-assets][error] No existe: $MASTER" >&2
  exit 1
fi

targets=(
  "zentrix-main-logo.png"
  "zentrix-menu-logo.png"
  "zentrix-sddm-logo.png"
  "zentrix-plymouth-logo.png"
  "zentrix-grub-logo.png"
  "zentrix-fastfetch-logo.png"
)

for target in "${targets[@]}"; do
  cp "$MASTER" "$LOGO_DIR/$target"
  echo "[sync-brand-assets] actualizado: $target"
done

echo "[sync-brand-assets] completado"
