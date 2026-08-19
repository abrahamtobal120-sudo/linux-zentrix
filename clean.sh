#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

safe_remove_dir() {
  local target="$1"
  local abs

  abs="$(realpath -m "$target")"
  if [[ "$abs" != "$PROJECT_ROOT"/* ]]; then
    printf '[clean][error] Ruta fuera del proyecto: %s\n' "$abs" >&2
    exit 1
  fi

  if [[ -d "$abs" ]]; then
    printf '[clean] Eliminando %s\n' "$abs"
    rm -rf -- "$abs"
  else
    printf '[clean] No existe %s, se omite\n' "$abs"
  fi
}

safe_remove_dir "$PROJECT_ROOT/work"
safe_remove_dir "$PROJECT_ROOT/out"
safe_remove_dir "$PROJECT_ROOT/.build"

printf '[clean] Limpieza completada\n'
