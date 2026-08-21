from __future__ import annotations

import json

from PySide6 import QtCore, QtWidgets

from core.parental import ParentalAgent
from core.parental_remote import RemoteParentalManager


class ParentalPage(QtWidgets.QWidget):
    def __init__(self, local: bool = False) -> None:
        super().__init__()
        self.agent = ParentalAgent()
        self.remote = RemoteParentalManager()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("Parental Control")
        title.setObjectName("sectionTitle")

        self.summary = QtWidgets.QLabel("Loading...")
        self.summary.setWordWrap(True)
        self.summary.setObjectName("mutedLabel")

        self.quick_actions = QtWidgets.QLabel("Waiting for policy...")
        self.quick_actions.setObjectName("mutedLabel")

        self.weekly_summary = QtWidgets.QLabel("Uso semanal: sin datos todavía")
        self.weekly_summary.setWordWrap(True)
        self.weekly_summary.setObjectName("mutedLabel")

        self.policy = QtWidgets.QPlainTextEdit()
        self.policy.setReadOnly(True)

        self.diagnostics = QtWidgets.QPlainTextEdit()
        self.diagnostics.setReadOnly(True)

        setup = QtWidgets.QGroupBox("Configurar Zentrix Cloud")
        setup_layout = QtWidgets.QVBoxLayout(setup)
        setup_intro = QtWidgets.QLabel(
            "Sigue estos pasos para conectar Zentrix con internet. No necesitas saber de servidores."
        )
        setup_intro.setWordWrap(True)
        setup_intro.setObjectName("mutedLabel")
        self.step_label = QtWidgets.QLabel("Paso 1 de 3: Escribe tu cuenta de Supabase")
        self.step_label.setObjectName("cardLabel")
        self.supabase_url_edit = QtWidgets.QLineEdit()
        self.supabase_url_edit.setPlaceholderText("https://xyzcompany.supabase.co")
        self.supabase_anon_key_edit = QtWidgets.QLineEdit()
        self.supabase_anon_key_edit.setPlaceholderText("Clave pública anon")
        self.supabase_anon_key_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.supabase_project_ref_edit = QtWidgets.QLineEdit()
        self.supabase_project_ref_edit.setPlaceholderText("xyzcompany")
        self.family_name_edit = QtWidgets.QLineEdit()
        self.family_name_edit.setPlaceholderText("Familia Zentrix")
        self.parent_user_edit = QtWidgets.QLineEdit()
        self.parent_user_edit.setPlaceholderText("Nombre del padre o madre")
        self.supabase_status = QtWidgets.QLabel("Aun no configurado")
        self.supabase_status.setObjectName("mutedLabel")
        save_cloud_button = QtWidgets.QPushButton("Guardar y continuar")
        save_cloud_button.clicked.connect(self._save_supabase_config)
        validate_cloud_button = QtWidgets.QPushButton("Comprobar conexión")
        validate_cloud_button.clicked.connect(self._validate_supabase_config)
        setup_layout.addWidget(setup_intro)
        setup_layout.addWidget(self.step_label)
        setup_layout.addWidget(QtWidgets.QLabel("1. Dirección de Supabase"))
        setup_layout.addWidget(self.supabase_url_edit)
        setup_layout.addWidget(QtWidgets.QLabel("2. Clave pública"))
        setup_layout.addWidget(self.supabase_anon_key_edit)
        setup_layout.addWidget(QtWidgets.QLabel("3. Identificación de proyecto"))
        setup_layout.addWidget(self.supabase_project_ref_edit)
        setup_layout.addWidget(QtWidgets.QLabel("4. Nombre de la familia"))
        setup_layout.addWidget(self.family_name_edit)
        setup_layout.addWidget(QtWidgets.QLabel("5. Quién es el padre o madre"))
        setup_layout.addWidget(self.parent_user_edit)
        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(save_cloud_button)
        button_row.addWidget(validate_cloud_button)
        setup_layout.addLayout(button_row)
        setup_layout.addWidget(self.supabase_status)

        controls = QtWidgets.QGroupBox("Admin controls")
        controls_layout = QtWidgets.QGridLayout(controls)
        self.users_edit = QtWidgets.QLineEdit()
        self.users_edit.setPlaceholderText("kid1,kid2")
        self.daily_limit_edit = QtWidgets.QSpinBox()
        self.daily_limit_edit.setRange(0, 1440)
        self.daily_limit_edit.setValue(180)

        self.allowed_hours_edit = QtWidgets.QLineEdit()
        self.allowed_hours_edit.setPlaceholderText("06:30-07:20, 17:45-21:30")
        self.blocked_hours_edit = QtWidgets.QLineEdit()
        self.blocked_hours_edit.setPlaceholderText("21:30-06:30, 14:00-16:00")
        schedule_help = QtWidgets.QLabel(
            "Horarios permitidos: solo se puede usar dentro de esos rangos. "
            "Horarios bloqueados: siempre se bloquean, incluso si coinciden con un rango permitido."
        )
        schedule_help.setWordWrap(True)
        schedule_help.setObjectName("mutedLabel")

        self.school_user_edit = QtWidgets.QLineEdit()
        self.school_user_edit.setPlaceholderText("kid1")
        self.apps_edit = QtWidgets.QPlainTextEdit()
        self.apps_edit.setPlaceholderText('[{"identifier":"/usr/bin/firefox","action":"allow"}]')
        self.apps_edit.setMaximumHeight(90)
        self.internet_edit = QtWidgets.QPlainTextEdit()
        self.internet_edit.setPlaceholderText('{"mode":"allow","allowed_domains":["wikipedia.org"]}')
        self.internet_edit.setMaximumHeight(90)
        save_policy_button = QtWidgets.QPushButton("Save policy")
        save_policy_button.clicked.connect(self._save_policy)
        lock_button = QtWidgets.QPushButton("Lock current user")
        lock_button.clicked.connect(self._lock_current_user)

        controls_layout.addWidget(QtWidgets.QLabel("Controlled users"), 0, 0)
        controls_layout.addWidget(self.users_edit, 0, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Daily limit"), 1, 0)
        controls_layout.addWidget(self.daily_limit_edit, 1, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Allowed hours"), 2, 0)
        controls_layout.addWidget(self.allowed_hours_edit, 2, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Blocked hours"), 3, 0)
        controls_layout.addWidget(self.blocked_hours_edit, 3, 1)
        controls_layout.addWidget(schedule_help, 4, 0, 1, 2)
        controls_layout.addWidget(QtWidgets.QLabel("School user"), 5, 0)
        controls_layout.addWidget(self.school_user_edit, 5, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Apps"), 6, 0)
        controls_layout.addWidget(self.apps_edit, 6, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Internet"), 7, 0)
        controls_layout.addWidget(self.internet_edit, 7, 1)
        controls_layout.addWidget(save_policy_button, 8, 0)
        controls_layout.addWidget(lock_button, 8, 1)

        layout.addWidget(title)
        layout.addWidget(self.summary)
        layout.addWidget(self.quick_actions)
        layout.addWidget(self.weekly_summary)
        layout.addWidget(setup)
        layout.addWidget(controls)
        layout.addWidget(QtWidgets.QLabel("Policy"))
        layout.addWidget(self.policy)
        layout.addWidget(QtWidgets.QLabel("Diagnostics"))
        layout.addWidget(self.diagnostics)

    @staticmethod
    def _format_minutes(minutes: int) -> str:
        minutes = max(0, int(minutes or 0))
        hours, mins = divmod(minutes, 60)
        if hours and mins:
            return f"{hours} h {mins} min"
        if hours:
            return f"{hours} h"
        return f"{mins} min"

    @staticmethod
    def _format_ranges(windows: list[dict]) -> str:
        ranges = []
        for window in windows or []:
            start = str(window.get("start", "")).strip()
            end = str(window.get("end", "")).strip()
            if start and end:
                ranges.append(f"{start}-{end}")
        return ", ".join(ranges)

    @staticmethod
    def _parse_ranges(text: str) -> list[dict[str, str]]:
        windows: list[dict[str, str]] = []
        for raw_range in text.split(","):
            value = raw_range.strip()
            if not value:
                continue
            if "-" not in value:
                raise ValueError(f"Rango inválido: {value}. Usa HH:MM-HH:MM")
            start, end = [part.strip() for part in value.split("-", 1)]
            for label, hhmm in (("inicio", start), ("fin", end)):
                parts = hhmm.split(":")
                if len(parts) != 2 or not all(part.isdigit() for part in parts):
                    raise ValueError(f"Hora de {label} inválida: {hhmm}")
                hour, minute = int(parts[0]), int(parts[1])
                if not 0 <= hour <= 23 or not 0 <= minute <= 59:
                    raise ValueError(f"Hora de {label} inválida: {hhmm}")
            windows.append({"start": start, "end": end})
        return windows

    def refresh(self) -> None:
        try:
            status = self.agent.status().__dict__
            policy = self.agent.show_policy()
            diagnostics = self.agent.diagnostics()
            cloud_config = self.remote.load_supabase_config()
            state = self.agent.store.load_state()
        except Exception as exc:
            self.summary.setText(f"No se pudo cargar Parental Control: {exc}")
            return

        self.summary.setText(
            f"Usuarios controlados: {', '.join(status.get('enabled_users', [])) or 'ninguno'}\n"
            f"Usuario actual: {status.get('current_user', '') or 'desconocido'}\n"
            f"Modo: {status.get('mode', 'normal')}"
        )
        self.quick_actions.setText(
            f"Restante: {status.get('remaining_minutes', 0)} min | "
            f"Usado hoy: {status.get('daily_used_minutes', 0)} min | "
            f"Bloqueado: {'si' if status.get('locked') else 'no'}"
        )

        weekly_parts = []
        state_users = state.get("users", {}) if isinstance(state, dict) else {}
        for user in policy.get("selected_users", []):
            user_state = state_users.get(user, {})
            weekly_parts.append(
                f"{user}: {self._format_minutes(int(user_state.get('weekly_used_minutes', 0) or 0))}"
            )
        self.weekly_summary.setText(
            "Tiempo acumulado esta semana: " + (" | ".join(weekly_parts) if weekly_parts else "sin usuarios controlados")
        )

        screen_time = policy.get("screen_time", {}) or {}
        self.users_edit.setText(",".join(policy.get("selected_users", [])))
        self.daily_limit_edit.setValue(int(screen_time.get("daily_limit_minutes", 180) or 0))
        self.allowed_hours_edit.setText(self._format_ranges(screen_time.get("allowed_hours", [])))
        self.blocked_hours_edit.setText(self._format_ranges(screen_time.get("blocked_hours", [])))
        school_mode_users = policy.get("school_mode_users", [])
        self.school_user_edit.setText(school_mode_users[0] if school_mode_users else "")
        self.apps_edit.setPlainText(json.dumps(policy.get("apps", []), indent=2))
        self.internet_edit.setPlainText(json.dumps(policy.get("internet", {}), indent=2))
        self.policy.setPlainText(json.dumps(policy, indent=2))
        self.diagnostics.setPlainText(json.dumps(diagnostics, indent=2))
        self.supabase_url_edit.setText(cloud_config.url)
        self.supabase_anon_key_edit.setText(cloud_config.anon_key)
        self.supabase_project_ref_edit.setText(cloud_config.project_ref)
        self.family_name_edit.setText(cloud_config.family_name)
        self.parent_user_edit.setText(cloud_config.parent_user)
        self.step_label.setText(
            "Paso 3 de 3: Revisa los datos y pulsa Guardar y continuar"
            if cloud_config.url
            else "Paso 1 de 3: Escribe tu cuenta de Supabase"
        )
        self.supabase_status.setText("Listo para conectar" if cloud_config.url else "Aun no configurado")

    def _save_policy(self) -> None:
        try:
            current_screen_time = dict(self.agent.show_policy().get("screen_time", {}) or {})
            current_screen_time.update(
                {
                    "daily_limit_minutes": int(self.daily_limit_edit.value()),
                    "allowed_hours": self._parse_ranges(self.allowed_hours_edit.text()),
                    "blocked_hours": self._parse_ranges(self.blocked_hours_edit.text()),
                }
            )
            payload = {
                "selected_users": [user.strip() for user in self.users_edit.text().split(",") if user.strip()],
                "school_mode_users": [self.school_user_edit.text().strip()] if self.school_user_edit.text().strip() else [],
                "screen_time": current_screen_time,
                "apps": json.loads(self.apps_edit.toPlainText() or "[]"),
                "internet": json.loads(self.internet_edit.toPlainText() or "{}"),
            }
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Parental Control", f"Policy inválida\n\n{exc}")
            return

        try:
            result = self.agent.save_policy_document(payload)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Parental Control", f"No se pudo guardar la política\n\n{exc}")
            return

        QtWidgets.QMessageBox.information(self, "Parental Control", json.dumps(result, indent=2))
        self.refresh()

    def _lock_current_user(self) -> None:
        try:
            current = self.agent.status().current_user
            if not current:
                raise RuntimeError("No current controlled user detected")
            self.agent.set_locked(current, True)
            self.refresh()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Parental Control", f"No se pudo bloquear\n\n{exc}")

    def _save_supabase_config(self) -> None:
        try:
            result = self.remote.save_supabase_config(
                self.supabase_url_edit.text(),
                self.supabase_anon_key_edit.text(),
                self.supabase_project_ref_edit.text(),
                self.family_name_edit.text(),
                self.parent_user_edit.text(),
            )
            validation = self.remote.validate_supabase_config()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Zentrix Cloud", f"No se pudo guardar la configuración\n\n{exc}")
            return

        message = json.dumps({"save": result, "validation": validation}, indent=2)
        QtWidgets.QMessageBox.information(self, "Zentrix Cloud", message)
        self.step_label.setText("Paso 3 de 3: Ya puedes vincular tu computadora")
        self.refresh()

    def _validate_supabase_config(self) -> None:
        validation = self.remote.validate_supabase_config()
        text = json.dumps(validation, indent=2)
        if validation.get("ok"):
            QtWidgets.QMessageBox.information(self, "Zentrix Cloud", text)
        else:
            QtWidgets.QMessageBox.warning(self, "Zentrix Cloud", text)
