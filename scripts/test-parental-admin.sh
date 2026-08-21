#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM_DIR="$PROJECT_ROOT/zentrix-platform"

cd "$PLATFORM_DIR"

if ! python3 -c 'import PySide6' >/dev/null 2>&1; then
  echo "[test-parental-admin][error] PySide6 no está disponible en este sistema." >&2
  exit 1
fi

exec sudo -E python3 - <<'PY'
import sys
from PySide6 import QtWidgets
from gui.parental_page import ParentalPage

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
window.setWindowTitle("Zentrix Parental Control — Admin")
window.resize(1100, 760)

scroll = QtWidgets.QScrollArea()
scroll.setWidgetResizable(True)
scroll.setHorizontalScrollBarPolicy(QtWidgets.Qt.ScrollBarPolicy.ScrollBarAsNeeded) if hasattr(QtWidgets, "Qt") else None

page = ParentalPage(local=True)
page.refresh()
scroll.setWidget(page)
window.setCentralWidget(scroll)
window.showMaximized()

sys.exit(app.exec())
PY
