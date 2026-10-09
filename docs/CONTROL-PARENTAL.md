# Control parental de Zinarix OS — Documento de diseño

> Brief de ingeniería para el sistema de control parental de Zinarix OS.
> Uso previsto: equipo de un hijo menor administrado por el padre.
> Este documento es la especificación; la implementación va por fases (ver "Forma de trabajo").

# Rol
Actúa como ingeniero senior de Linux y seguridad. Diseña e implementa un sistema de control parental para Arch Linux.

# Contexto y modelo de amenaza
- Equipo con Arch Linux. Lo administro yo de forma remota, desde el celular o mi computadora, incluso fuera de casa.
- El usuario controlado tiene conocimientos técnicos: programa, usa mucho la terminal y crea páginas y apps.
- Decisión central: él CONSERVA root/sudo para TODO su uso normal (instalar paquetes, programar, Docker/contenedores, configurar red, etc.). NO se lo quito ni se lo restrinjo en lo cotidiano.
- La ÚNICA excepción: no puede apagar, editar ni desinstalar el control parental sin mi contraseña de administrador.
- Principio honesto que debe guiar el diseño: la seguridad NO viene de ocultar comandos ni de poner "muchos pasos". Con root, él puede leer el código y la configuración. La protección viene de una frontera de permisos real: una autoridad que su sudo no cruza. Diséñalo así, no con oscuridad.
- Zona horaria: America/Mexico_City.

# Cómo se logra la frontera (mecanismo, no ocultamiento)
Todo lo que sea "control parental" queda bajo una etiqueta protegida que su sudo no alcanza, aunque sea root para el resto. Propón y usa el mecanismo más sólido para Arch; evalúa estas opciones y recomienda:
- SELinux o AppArmor con una política donde su dominio (incluido root para su usuario) no pueda detener, matar, editar ni relabelear los procesos, archivos y unidades del control parental, ni desactivar el propio MAC (p. ej. secure_mode_policyload en SELinux). Su sudo sigue siendo root para todo lo demás.
- Un administrador aparte (cuenta mía) y la cuenta root real reservada para mí; su "root" es sudo dentro de un contexto confinado.
- Protección de arranque para que no evada el MAC apagándolo al inicio:
  - Secure Boot con mis llaves y una UKI firmada con la línea de comandos del kernel incrustada, para impedir que agregue enforcing=0, selinux=0, apparmor=0 o init=/bin/bash.
  - Gestor de arranque con contraseña.
  - Si hay TPM 2.0, LUKS ligado al TPM (PCR 7) para que arrancar desde USB no dé acceso al disco. Si no hay TPM, dímelo y propón la mejor alternativa.
- Sé explícito sobre el límite físico: con acceso físico y tiempo (reinstalar desde USB, sacar el disco) el control se puede vencer. Eso se cubre con detección (más abajo), no con ocultamiento.

# Funciones del control parental
## Tiempo de pantalla
- Límite diario por día de la semana más franjas horarias permitidas.
- Contar solo tiempo activo (IdleHint/LockedHint de logind), sumando sesiones gráficas, TTY y SSH.
- Avisos a 15, 5 y 1 minuto antes de terminar.
- Al agotarse: bloquear la sesión, 2 minutos de gracia y cerrar sus sesiones.
- Módulo PAM que impide iniciar sesión sin tiempo o fuera de horario. Solo para su usuario; mi cuenta nunca queda bloqueada.
- Contador persistente entre reinicios, reinicio a medianoche, a prueba de cambios de hora.
- Indicador en su escritorio con el tiempo restante.
- Desde remoto: dar o quitar tiempo, pausar (para tareas), bloquear de inmediato y modo libre temporal.

## Filtro web
- Lista blanca o lista negra, editable desde el panel.
- Aplicarlo a nivel de red local para su UID (resolver DNS local + nftables con meta skuid), para que valga en cualquier programa, no solo el navegador. Forzar su DNS al resolver local y bloquear DoT, DoH, VPN, proxies y Tor.
- El filtro es parte del control protegido: su sudo no puede desactivarlo ni cambiar sus reglas.
- Subdominios y comodines, punycode, IPv4 e IPv6.
- Búsqueda segura forzada y YouTube en modo restringido, activables por separado.
- Categorías activables con un clic: Programación (GitHub, repos de Arch y AUR, npm, PyPI, Stack Overflow, MDN), IA (solo las que yo apruebe) y Escuela.
- Registro de dominios bloqueados recientes, con botón "aprobar" en el panel.
- Complemento en el navegador (Firefox y Chromium/Chrome): políticas administradas para desactivar el DoH del navegador y permitir solo extensiones aprobadas, con página de bloqueo y botón "pedir acceso".

## Solicitudes
- Él puede pedir más tiempo, un sitio o desbloqueo temporal.
- Me llega al celular con botones Aprobar / Rechazar (ntfy con acciones o bot de Telegram).

# Detección (para el límite físico que ningún permiso cubre)
- Heartbeat periódico a un servicio tipo healthchecks.io o a una Raspberry Pi. Si dentro del horario permitido deja de reportar, me llega una alerta.
- auditd sobre los archivos, unidades y binarios del control; verificación de integridad al arrancar.
- Opcional, segunda capa independiente: filtro DNS en el router o una Raspberry Pi (AdGuard Home), que sigue aplicando aunque reinstale el sistema. Dame los pasos si lo quiero.
- Falla segura: si el servicio cae, las reglas de red de su usuario se mantienen (bloqueado para él, nunca para mí ni para el sistema).
- Recuperación: procedimiento para que yo desactive todo en una emergencia o si pierdo el acceso remoto.

# Panel y acceso remoto
- Panel web en español, pensado para el celular: tiempo de hoy, historial semanal, límites, listas, solicitudes, alertas de manipulación y registro de eventos.
- Acceso solo por Tailscale, con ACL para que solo mis dispositivos lleguen. Contraseña con argon2, sesiones con expiración, CSRF y límite de intentos.

# Requisitos técnicos
- Go (preferido: un binario, bajo consumo) o Python 3, dependencias mínimas.
- Componentes: daemon del control (parentald) bajo la etiqueta protegida; indicador sin privilegios en su sesión (socket Unix con SO_PEERCRED); módulo PAM; panel web.
- Configuración en /etc/parental/ (root:root, 600) y estado en /var/lib/parental/, ambos protegidos por la política MAC.
- Unidades systemd con reinicio automático y sandboxing.
- Instalación con PKGBUILD (makepkg -si) más un script de configuración inicial que instale la política MAC y firme la UKI.
- Pruebas: unitarias (conteo de tiempo, coincidencia de dominios); script de auditoría que como root intente vencer el control y reporte pasa/falla; checklist manual de pruebas físicas.

# Forma de trabajo
1. Preguntas primero; luego el plan (arquitectura, árbol de archivos, SELinux vs AppArmor, arranque/TPM) con pros y contras. Esperar OK antes de programar.
2. Verificar que la cuenta de administrador y el root funcionan ANTES de activar el confinamiento.
3. Fases: (1) frontera de permisos (MAC + arranque) y cuenta admin; (2) tiempo de pantalla, PAM e indicador; (3) filtro web y políticas de navegador; (4) panel, solicitudes, detección y auditoría.
4. Entregables: código y política MAC; config de ejemplo; guías de instalación y uso desde el celular; sección honesta de limitaciones.

# Preguntas antes de empezar
- ¿SELinux o AppArmor?
- ¿El equipo tiene TPM 2.0 y Secure Boot activable?
- ¿Para qué usa sudo normalmente?
- ¿Qué escritorio y navegadores usa?
- ¿Qué horarios y límites quieres para empezar?

Defaults si no respondo: AppArmor; sin TPM, Secure Boot con UKI firmada + heartbeat; KDE con Firefox y Chromium; lista blanca con categoría Programación; L–V 2 h (16:00–20:00) y S–D 4 h (10:00–21:00).
