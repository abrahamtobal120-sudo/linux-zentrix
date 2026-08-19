#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
class _MissingQtModule:
    """Placeholder usado cuando PySide6 no está disponible."""
    pass
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ModuleNotFoundError:
    class _MissingQtType:
        def __init__(self, *args, **kwargs) -> None:
            raise ModuleNotFoundError("PySide6 is required for the Zentrix Control Center GUI")

    class _MissingQtCore:
        @staticmethod
        def Signal(*args, **kwargs):
            return None

    class _MissingQtModule:
        def __getattr__(self, _name: str):
            return _MissingQtType

    QtCore = _MissingQtCore()
    QtGui = _MissingQtModule()
    QtWidgets = _MissingQtModule()

from api.client import build_client, run


APP_TITLE = "Zentrix Control Center"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--bus", choices=["system", "session"], default="system")
    parser.add_argument("--local", action="store_true", help="Run against the in-process development backend")
    return parser.parse_args()


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def launch_command(command: list[str], parent: QtWidgets.QWidget | None = None) -> None:
    try:
        subprocess.Popen(command)
    except Exception as exc:
        QtWidgets.QMessageBox.critical(parent, APP_TITLE, f"No se pudo ejecutar {' '.join(command)}\n\n{exc}")


@dataclass
class Snapshot:
    status: dict
    health: dict
    profiles: list[str]
    modules: list[str]
    history: list[dict]


class DashboardPage(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.cards: dict[str, QtWidgets.QLabel] = {}
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(14)

        hero = QtWidgets.QFrame()
        hero.setObjectName("heroPanel")
        hero_layout = QtWidgets.QVBoxLayout(hero)
        title = QtWidgets.QLabel("ZENTRIX")
        title.setObjectName("heroTitle")
        subtitle = QtWidgets.QLabel("System dashboard")
        subtitle.setObjectName("heroSubtitle")
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)

        grid_wrap = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(grid_wrap)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        names = [
            ("System Health", "health"),
            ("Current Profile", "profile"),
            ("Updates", "updates"),
            ("Firewall", "firewall"),
            ("Snapshot", "snapshot"),
            ("Telemetry", "telemetry"),
        ]
        for index, (label, key) in enumerate(names):
            card = self._make_card(label)
            self.cards[key] = card.findChild(QtWidgets.QLabel, f"value_{key}")
            row = index // 2
            col = index % 2
            grid.addWidget(card, row, col)

        layout.addWidget(hero)
        layout.addWidget(grid_wrap)
        layout.addStretch(1)

    def _make_card(self, label_text: str) -> QtWidgets.QFrame:
        key = label_text.lower().replace(" ", "_")
        if label_text == "System Health":
            key = "health"
        elif label_text == "Current Profile":
            key = "profile"
        elif label_text == "Updates":
            key = "updates"
        elif label_text == "Firewall":
            key = "firewall"
        elif label_text == "Snapshot":
            key = "snapshot"
        elif label_text == "Telemetry":
            key = "telemetry"

        card = QtWidgets.QFrame()
        card.setObjectName("dashboardCard")
        layout = QtWidgets.QVBoxLayout(card)
        label = QtWidgets.QLabel(label_text)
        label.setObjectName("cardLabel")
        value = QtWidgets.QLabel("Loading...")
        value.setObjectName(f"value_{key}")
        layout.addWidget(label)
        layout.addWidget(value)
        return card

    def update_view(self, snapshot: Snapshot) -> None:
        self.cards["health"].setText(snapshot.health.get("system_health", "Unknown"))
        self.cards["profile"].setText(snapshot.status.get("profile", "Unknown"))
        self.cards["updates"].setText("Check from Zentrix Update")
        self.cards["firewall"].setText("Protected")
        self.cards["snapshot"].setText(snapshot.health.get("snapshot", "Unknown"))
        telemetry = "OFF" if not snapshot.status.get("telemetry", False) else "ON"
        self.cards["telemetry"].setText(telemetry)


class ProfilesPage(QtWidgets.QWidget):
    apply_requested = QtCore.Signal(str, bool)
    restore_requested = QtCore.Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._profiles: list[str] = []
        self._current_profile = "normal"

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("Zentrix Profiles")
        title.setObjectName("sectionTitle")

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.currentTextChanged.connect(self._on_selected_profile)

        self.preview = QtWidgets.QPlainTextEdit()
        self.preview.setReadOnly(True)

        self.history_box = QtWidgets.QPlainTextEdit()
        self.history_box.setReadOnly(True)
        self.history_box.setMaximumHeight(180)

        buttons = QtWidgets.QHBoxLayout()
        self.preview_button = QtWidgets.QPushButton("Preview Changes")
        self.apply_button = QtWidgets.QPushButton("Apply Profile")
        self.restore_button = QtWidgets.QPushButton("Restore Previous Configuration")
        self.apply_button.setObjectName("ctaButton")
        self.preview_button.clicked.connect(self._preview_selected)
        self.apply_button.clicked.connect(self._apply_selected)
        self.restore_button.clicked.connect(lambda: self.restore_requested.emit(False))
        buttons.addWidget(self.preview_button)
        buttons.addWidget(self.apply_button)
        buttons.addWidget(self.restore_button)
        buttons.addStretch(1)

        layout.addWidget(title)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.preview)
        layout.addWidget(QtWidgets.QLabel("History"))
        layout.addWidget(self.history_box)
        layout.addLayout(buttons)

    def update_view(self, snapshot: Snapshot) -> None:
        self._profiles = snapshot.profiles
        self._current_profile = snapshot.status.get("profile", "normal")
        self.list_widget.clear()
        self.list_widget.addItems(snapshot.profiles)
        self.restore_button.setEnabled(bool(snapshot.status.get("restorable")))
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.text() == self._current_profile:
                item.setText(f"{item.text()} (current)")
                self.list_widget.setCurrentRow(index)
                break
        if snapshot.history:
            recent = json.dumps(snapshot.history[-5:], indent=2)
        else:
            recent = "No profile history yet."
        self.history_box.setPlainText(recent)

    def _clean_name(self, text: str) -> str:
        return text.replace(" (current)", "")

    def _on_selected_profile(self, text: str) -> None:
        if not text:
            self.preview.setPlainText("")
            return
        name = self._clean_name(text)
        self.preview.setPlainText(
            f"Selected profile: {name}\n\n"
            "Use Preview Changes to inspect the current dry-run plan before applying.\n"
            "All profile actions in this phase are reversible and conservative by default."
        )

    def _preview_selected(self) -> None:
        text = self.list_widget.currentItem().text() if self.list_widget.currentItem() else ""
        if text:
            self.apply_requested.emit(self._clean_name(text), True)

    def _apply_selected(self) -> None:
        text = self.list_widget.currentItem().text() if self.list_widget.currentItem() else ""
        if text:
            self.apply_requested.emit(self._clean_name(text), False)

    def show_result(self, result: dict) -> None:
        self.preview.setPlainText(json.dumps(result, indent=2))


class ActionsPage(QtWidgets.QWidget):
    def __init__(self, title_text: str, summary: str, actions: list[tuple[str, str, list[str]]]) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        title = QtWidgets.QLabel(title_text)
        title.setObjectName("sectionTitle")
        info = QtWidgets.QLabel(summary)
        info.setWordWrap(True)
        info.setObjectName("mutedLabel")

        layout.addWidget(title)
        layout.addWidget(info)

        for label, description, command in actions:
            panel = QtWidgets.QFrame()
            panel.setObjectName("actionPanel")
            panel_layout = QtWidgets.QHBoxLayout(panel)
            text_wrap = QtWidgets.QVBoxLayout()
            head = QtWidgets.QLabel(label)
            head.setObjectName("cardLabel")
            body = QtWidgets.QLabel(description)
            body.setWordWrap(True)
            body.setObjectName("mutedLabel")
            button = QtWidgets.QPushButton("Open")
            button.clicked.connect(lambda _checked=False, cmd=command: launch_command(cmd, self))
            text_wrap.addWidget(head)
            text_wrap.addWidget(body)
            panel_layout.addLayout(text_wrap)
            panel_layout.addStretch(1)
            panel_layout.addWidget(button)
            layout.addWidget(panel)

        layout.addStretch(1)


class AboutPage(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("About Zentrix Control Center")
        title.setObjectName("sectionTitle")
        text = QtWidgets.QLabel(
            "This base Control Center is the first user-facing shell of Zentrix Core.\n\n"
            "It talks to the daemon over D-Bus, previews changes before applying them,\n"
            "and keeps privileged operations behind controlled system services."
        )
        text.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch(1)


class ControlCenter(QtWidgets.QMainWindow):
    def __init__(self, bus: str, local: bool = False) -> None:
        super().__init__()
        self.local = local
        self.client = build_client(bus=bus, local=local)
        self.setWindowTitle(APP_TITLE)
        self.resize(1200, 760)
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        root = QtWidgets.QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")
        side_layout = QtWidgets.QVBoxLayout(sidebar)

        logo = QtWidgets.QLabel("ZENTRIX")
        logo.setObjectName("sidebarTitle")
        sub = QtWidgets.QLabel("Control Center")
        sub.setObjectName("sidebarSubtitle")

        self.nav = QtWidgets.QListWidget()
        self.nav.addItems(["Dashboard", "Profiles", "Updates", "Drivers", "About"])
        self.nav.currentRowChanged.connect(self._switch_page)

        refresh_button = QtWidgets.QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)

        side_layout.addWidget(logo)
        side_layout.addWidget(sub)
        side_layout.addSpacing(10)
        side_layout.addWidget(self.nav)
        side_layout.addStretch(1)
        side_layout.addWidget(refresh_button)

        self.pages = QtWidgets.QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.profiles_page = ProfilesPage()
        self.profiles_page.apply_requested.connect(self._apply_profile)
        self.profiles_page.restore_requested.connect(self._restore_previous)
        self.updates_page = ActionsPage(
            "Zentrix Update",
            "Use Arch-standard update flows with snapshot-aware tooling in later phases.",
            [
                ("Open Zentrix Update", "Launch the existing update workflow.", ["konsole", "-e", "zentrix-update"]),
                ("View Health", "Inspect current health information from Zentrix Core.", ["konsole", "-e", "zentrix-health"]),
            ],
        )
        self.drivers_page = ActionsPage(
            "Zentrix Driver Center",
            "Driver detection and recommendations are modular and will grow in later phases.",
            [
                ("Scan My Computer", "Run the driver command-line scaffold.", ["konsole", "-e", "zentrix-drivers"]),
                ("Search Online Drivers", "Reserved safe entry point for trusted-source search.", ["konsole", "-e", "zentrixctl", "module", "info", "drivers"]),
            ],
        )
        self.about_page = AboutPage()

        for page in [self.dashboard_page, self.profiles_page, self.updates_page, self.drivers_page, self.about_page]:
            self.pages.addWidget(page)

        root.addWidget(sidebar, 1)
        root.addWidget(self.pages, 3)
        self.setCentralWidget(central)
        self.nav.setCurrentRow(0)
        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #0b0f16; }
            QFrame#sidebar { background: #121826; border: 1px solid #233047; border-radius: 12px; }
            QLabel#sidebarTitle { color: #f3f7ff; font-size: 28px; font-weight: 800; }
            QLabel#sidebarSubtitle { color: #8fa4c7; font-size: 14px; }
            QLabel#heroTitle { color: #f3f7ff; font-size: 34px; font-weight: 800; }
            QLabel#heroSubtitle { color: #8fa4c7; font-size: 15px; }
            QLabel#sectionTitle { color: #eef4ff; font-size: 24px; font-weight: 700; }
            QLabel#cardLabel { color: #9db1d1; font-size: 14px; }
            QLabel#mutedLabel { color: #a7b6cc; }
            QFrame#heroPanel, QFrame#dashboardCard, QFrame#actionPanel {
                background: #121826;
                border: 1px solid #233047;
                border-radius: 12px;
            }
            QListWidget {
                background: #0f1520;
                color: #dbe8ff;
                border: 1px solid #233047;
                border-radius: 10px;
                padding: 6px;
            }
            QListWidget::item { padding: 10px; border-radius: 8px; }
            QListWidget::item:selected { background: #1f8bff; color: white; }
            QStackedWidget, QPlainTextEdit {
                background: #0f1520;
                color: #e8eef8;
                border: 1px solid #233047;
                border-radius: 10px;
            }
            QPushButton {
                background: #1c2637;
                color: #ecf2ff;
                border: 1px solid #32445e;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover { background: #243249; }
            QPushButton#ctaButton { background: #1f8bff; border-color: #58a8ff; font-weight: 700; }
            QPushButton#ctaButton:hover { background: #2b96ff; }
            """
        )

    def _switch_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)

    def refresh(self) -> None:
        try:
            snapshot = Snapshot(
                status=run(self.client.status()),
                health=run(self.client.health()),
                profiles=run(self.client.list_profiles()),
                modules=run(self.client.list_modules()),
                history=run(self.client.history()),
            )
        except Exception as exc:
            QtWidgets.QMessageBox.warning(
                self,
                APP_TITLE,
                "No se pudo conectar con Zentrix Core.\n\n"
                f"{exc}\n\n"
                "Puedes iniciar el daemon en desarrollo con:\n"
                "python daemon/main.py --bus session\n\n"
                "O abrir la interfaz en modo local con:\n"
                "python gui/control_center.py --local",
            )
            return

        self.dashboard_page.update_view(snapshot)
        self.profiles_page.update_view(snapshot)

    def _apply_profile(self, name: str, dry_run: bool) -> None:
        try:
            result = run(self.client.preview_profile(name)) if dry_run else run(self.client.apply_profile(name, False))
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, APP_TITLE, f"No se pudo aplicar el perfil {name}\n\n{exc}")
            return

        self.profiles_page.show_result(result)
        if not dry_run:
            self.refresh()

    def _restore_previous(self, dry_run: bool) -> None:
        try:
            result = run(self.client.restore_previous_profile(dry_run))
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, APP_TITLE, f"No se pudo restaurar la configuracion previa\n\n{exc}")
            return
        self.profiles_page.show_result(result)
        if result.get("ok") and not dry_run:
            self.refresh()


def main() -> int:
    if isinstance(QtWidgets, _MissingQtModule):
        print("PySide6 no esta instalado. Instala las dependencias de zentrix-platform para usar la GUI.")
        print("Sigue disponible el modo local CLI con: python3 cli/main.py --local status")
        return 1

    args = parse_args()
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setWindowIcon(QtGui.QIcon.fromTheme("preferences-system"))
    window = ControlCenter(bus=args.bus, local=args.local)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
