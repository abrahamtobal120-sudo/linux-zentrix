#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$PROJECT_ROOT/out"
DISK_DIR="$PROJECT_ROOT/.build/qemu"
DISK_PATH="$DISK_DIR/zentrix-test.qcow2"
DISK_SIZE_GB="64"
MODE="live"
BOOT_MODE="iso"
MEMORY_MB="4096"
CPU_COUNT="4"
OVMF_CODE="/usr/share/OVMF/x64/OVMF_CODE.fd"
OVMF_VARS_TEMPLATE="/usr/share/OVMF/x64/OVMF_VARS.fd"
OVMF_VARS="$DISK_DIR/OVMF_VARS.fd"

if [[ "${1:-}" == "--install" ]]; then
  MODE="install"
fi

if [[ "${1:-}" == "--boot-installed" ]]; then
  MODE="install"
  BOOT_MODE="disk"
fi

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    printf '[qemu][error] Falta comando requerido: %s\n' "$1" >&2
    exit 1
  }
}

require_command qemu-system-x86_64
require_command qemu-img

if [[ ! -d "$OUT_DIR" ]]; then
  printf '[qemu][error] No existe el directorio out/. Ejecuta ./build.sh primero.\n' >&2
  exit 1
fi

ISO_PATH="$(find "$OUT_DIR" -maxdepth 1 -type f -name '*.iso' -printf '%T@ %p\n' | sort -nr | awk 'NR==1{print $2}')"

if [[ -z "${ISO_PATH:-}" ]]; then
  printf '[qemu][error] No se encontro ninguna ISO en out/.\n' >&2
  exit 1
fi

printf '[qemu] Iniciando prueba con ISO: %s\n' "$ISO_PATH"

if [[ "$MODE" == "install" ]]; then
  mkdir -p "$DISK_DIR"
  if [[ ! -f "$DISK_PATH" ]]; then
    printf '[qemu] Creando disco de prueba: %s (%sG)\n' "$DISK_PATH" "$DISK_SIZE_GB"
    qemu-img create -f qcow2 "$DISK_PATH" "${DISK_SIZE_GB}G" >/dev/null
  else
    printf '[qemu] Usando disco existente: %s\n' "$DISK_PATH"
  fi

  if [[ -f "$OVMF_CODE" && -f "$OVMF_VARS_TEMPLATE" ]]; then
    if [[ ! -f "$OVMF_VARS" ]]; then
      cp "$OVMF_VARS_TEMPLATE" "$OVMF_VARS"
    fi
  fi
fi

qemu_common_args=(
  -enable-kvm
  -m "$MEMORY_MB"
  -smp "$CPU_COUNT"
  -cpu host
  -vga virtio
  -display gtk,gl=on
  -device ich9-intel-hda -device hda-duplex
  -netdev user,id=n1 -device virtio-net-pci,netdev=n1
)

if [[ -f "$OVMF_CODE" && -f "$OVMF_VARS" ]]; then
  qemu_common_args+=(
    -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE"
    -drive if=pflash,format=raw,file="$OVMF_VARS"
  )
fi

if [[ "$MODE" == "install" && "$BOOT_MODE" == "iso" ]]; then
  qemu-system-x86_64 \
    "${qemu_common_args[@]}" \
    -cdrom "$ISO_PATH" \
    -boot d \
    -drive file="$DISK_PATH",format=qcow2,if=virtio
elif [[ "$MODE" == "install" && "$BOOT_MODE" == "disk" ]]; then
  qemu-system-x86_64 \
    "${qemu_common_args[@]}" \
    -boot c \
    -drive file="$DISK_PATH",format=qcow2,if=virtio
else
  qemu-system-x86_64 \
    "${qemu_common_args[@]}" \
    -cdrom "$ISO_PATH" \
    -boot d
fi
