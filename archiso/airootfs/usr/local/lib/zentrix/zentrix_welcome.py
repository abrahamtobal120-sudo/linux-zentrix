#!/usr/bin/env python3
import subprocess
import sys
from PySide6 import QtCore, QtGui, QtWidgets

APP_TITLE = "Zentrix Welcome"

SECTIONS = {
    "Primeros pasos": (
        "Welcome to Zentrix\n\n"
        "by Abraham Tobal\n\n"
        "Esta guia te ayuda a comenzar rapido con un entorno limpio y moderno."
    ),
    "Conectarse a internet": (
        "Abre el administrador de red para conectarte por Wi-Fi o cable.\n\n"
        "Consejo: revisa el icono de red en la barra inferior."
    ),
    "Actualizar Zentrix": (
        "Zentrix usa actualizaciones seguras con pacman.\n\n"
        "Recomendado: ejecutar zentrix-update desde una terminal."
    ),
    "Instalar aplicaciones": (
        "Puedes instalar software con pacman y, opcionalmente, con soporte AUR en fases posteriores.\n\n"
        "Tambien puedes usar Discover cuando este disponible."
    ),
    "Configurar apariencia": (
        "Personaliza tema, iconos, fuentes y efectos desde configuracion de KDE."
    ),
    "Informacion del sistema": (
        "Consulta version, kernel, memoria y paquetes con zentrix-info y fastfetch."
    ),
    "Acerca de Zentrix": (
        "Zentrix by Abraham Tobal\n"
        "Version 1.0\n"
        "Base: Arch Linux\n"
        "Desktop: KDE Plasma"
    ),
}


def command_exists(name: str) -> bool:
    return subprocess.call(
        ["bash", "-lc", f"command -v {name} >/dev/null 2>&1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) == 0


def run_command(cmd):
    try:
        subprocess.Popen(cmd)
    except Exception as exc:
        QtWidgets.QMessageBox.critical(None, APP_TITLE, f"No se pudo ejecutar: {' '.join(cmd)}\n\n{exc}")


class WelcomeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(980, 600)
        self._build_ui()

    def _build_ui(self):
        central = QtWidgets.QWidget(self)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header = QtWidgets.QFrame()
        header.setObjectName("headerPanel")
        header_layout = QtWidgets.QHBoxLayout(header)

        title_wrap = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Welcome to Zentrix")
        title.setObjectName("titleLabel")
        subtitle = QtWidgets.QLabel("by Abraham Tobal")
        subtitle.setObjectName("subtitleLabel")
        title_wrap.addWidget(title)
        title_wrap.addWidget(subtitle)

        header_layout.addLayout(title_wrap)
        header_layout.addStretch(1)

        install_cta = QtWidgets.QPushButton("Install Zentrix")
        install_cta.setObjectName("ctaButton")
        install_cta.clicked.connect(lambda: run_command(["zentrix-install"]))
        header_layout.addWidget(install_cta)

        content_wrap = QtWidgets.QHBoxLayout()
        left_panel = QtWidgets.QFrame()
        left_panel.setMinimumWidth(280)
        left_panel.setObjectName("leftPanel")
        left_layout = QtWidgets.QVBoxLayout(left_panel)

        self.section_list = QtWidgets.QListWidget()
        self.section_list.addItems(list(SECTIONS.keys()))
        self.section_list.currentTextChanged.connect(self.on_section_change)

        left_layout.addWidget(QtWidgets.QLabel("Secciones"))
        left_layout.addWidget(self.section_list)

        right_panel = QtWidgets.QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QtWidgets.QVBoxLayout(right_panel)

        self.content = QtWidgets.QTextBrowser()
        self.content.setOpenExternalLinks(True)

        actions = QtWidgets.QHBoxLayout()
        btn_network = QtWidgets.QPushButton("Conectarse")
        btn_update = QtWidgets.QPushButton("Actualizar Zentrix")
        btn_install = QtWidgets.QPushButton("Instalar Zentrix")
        btn_apps = QtWidgets.QPushButton("Instalar Apps")
        btn_appearance = QtWidgets.QPushButton("Apariencia")
        btn_info = QtWidgets.QPushButton("System Info")

        btn_network.clicked.connect(self.open_network_settings)
        btn_update.clicked.connect(lambda: run_command(["konsole", "-e", "zentrix-update"]))
        btn_install.clicked.connect(lambda: run_command(["zentrix-install"]))
        btn_apps.clicked.connect(self.open_software_center)
        btn_appearance.clicked.connect(lambda: run_command(["systemsettings", "kcm_lookandfeel"]))
        btn_info.clicked.connect(lambda: run_command(["konsole", "-e", "zentrix-info"]))

        for b in [btn_network, btn_update, btn_install, btn_apps, btn_appearance, btn_info]:
            actions.addWidget(b)

        right_layout.addWidget(self.content)
        right_layout.addLayout(actions)

        content_wrap.addWidget(left_panel, 1)
        content_wrap.addWidget(right_panel, 2)

        root.addWidget(header)
        root.addLayout(content_wrap)

        self.setCentralWidget(central)
        self.section_list.setCurrentRow(0)

        self.setStyleSheet(
            """
            QMainWindow { background: #0c1017; }
            QFrame#headerPanel { background: #111826; border: 1px solid #24324a; border-radius: 10px; }
            QFrame#leftPanel { background: #151b25; border: 1px solid #233047; border-radius: 10px; }
            QFrame#rightPanel { background: #141a23; border: 1px solid #233047; border-radius: 10px; }
            QLabel#titleLabel { color: #e8eef9; font-size: 30px; font-weight: 700; }
            QLabel#subtitleLabel { color: #9eb0ca; font-size: 15px; }
            QListWidget { background: #101621; color: #d6deed; border: 1px solid #233047; border-radius: 8px; }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background: #1f8bff; color: #ffffff; border-radius: 4px; }
            QTextBrowser { background: #0f151f; color: #dbe7fb; border: 1px solid #233047; border-radius: 8px; font-size: 15px; }
            QPushButton { background: #1d2738; color: #e7edf9; border: 1px solid #31435f; border-radius: 8px; padding: 7px 10px; }
            QPushButton:hover { background: #243249; }
            QPushButton:pressed { background: #1f8bff; }
            QPushButton#ctaButton { background: #1f8bff; border: 1px solid #4fa4ff; font-weight: 700; min-height: 34px; padding: 8px 14px; }
            QPushButton#ctaButton:hover { background: #2a96ff; }
            """
        )

    def on_section_change(self, name):
        text = SECTIONS.get(name, "")
        self.content.setText(text)

    def open_software_center(self):
        if command_exists("plasma-discover"):
            run_command(["plasma-discover"])
        else:
            QtWidgets.QMessageBox.information(
                self,
                APP_TITLE,
                "Discover no esta disponible en esta imagen.\nUsa pacman desde terminal por ahora.",
            )

    def open_network_settings(self):
        if command_exists("systemsettings"):
            run_command(["systemsettings", "kcm_networkmanagement"])
        elif command_exists("nm-connection-editor"):
            run_command(["nm-connection-editor"])
        else:
            QtWidgets.QMessageBox.information(
                self,
                APP_TITLE,
                "No se encontro herramienta grafica de red disponible.",
            )


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)

    window = WelcomeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
