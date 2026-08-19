# Zentrix by Abraham Tobal

Proyecto para construir una distribucion Linux personalizada llamada **Zentrix by Abraham Tobal**, basada en Arch Linux, usando **Archiso**.

## Estado del proyecto

Este repositorio esta organizado por fases para permitir un desarrollo mantenible desde Visual Studio Code.

Nueva arquitectura modular de siguiente etapa:
- `zentrix-platform/` contiene Zentrix Core (daemon, API, CLI, modules, profiles, systemd, polkit).
- Ver roadmap: `docs/ZENTRIX-PLATFORM-ROADMAP.md`.
- Control Center base: `zentrix-platform/gui/control_center.py`.
- Motor local modular y registro de módulos añadidos en `zentrix-platform/core/engine.py`.
- Entradas de prueba de runtime disponibles para validar perfiles desde Python.

- Fase 1: Estructura del repositorio + base funcional de Archiso (completada)
- Fase 2: Perfil Archiso funcional para ISO Live (completada, baseline)
- Fase 3: ISO minima que arranque (preparada, pendiente validacion en host con archiso)
- Fase 4: Integracion KDE Plasma (implementada, pendiente validacion en ISO real)
- Fase 5: Integracion SDDM (implementada, pendiente validacion en ISO real)
- Fase 6: Branding Zentrix (implementada en componentes activos, pendiente validacion en ISO real)
- Fase 7: Plymouth y GRUB (implementada en perfil, pendiente validacion en ISO real)
- Fase 8: Aplicaciones Zentrix (implementada en perfil, pendiente validacion en ISO real)
- Fase 9: Integracion Calamares (implementada en perfil, pendiente validacion en ISO real)
- Fase 10: Pruebas de instalacion (scripts listos, pendiente ejecucion completa en host con archiso)

## Identidad del sistema

- Nombre completo: Zentrix by Abraham Tobal
- Nombre corto: Zentrix
- ID: zentrix
- Version inicial: 1.0
- Arquitectura: x86_64
- Base: Arch Linux

## Requisitos

Sistema anfitrion recomendado: Arch Linux o derivado compatible con Archiso.

Nota: si tus repos no incluyen `calamares`, el build generara una ISO Live funcional pero sin instalador grafico integrado.

Instala dependencias minimas:

```bash
sudo pacman -S --needed archiso git qemu-full rsync
```

Para agregar Calamares de forma limpia en Arch, lo recomendable es usar un repo local con el paquete ya construido y apuntar el build a ese repo con `ZENTRIX_LOCAL_REPO`.

Ejemplo:

```bash
mkdir -p ~/zentrix-localrepo
# Copia aqui calamares-*.pkg.tar.zst y sus dependencias no oficiales si hacen falta
repo-add ~/zentrix-localrepo/zentrix-local.db.tar.gz ~/zentrix-localrepo/*.pkg.tar.zst

cd zentrix-os
ZENTRIX_LOCAL_REPO=~/zentrix-localrepo ./build.sh
```

Si no tienes el paquete aun, primero debes construir `calamares` para Arch o exportarlo desde una fuente compatible hacia ese repo local.

## Estructura principal

```text
zentrix-os/
├── README.md
├── build.sh
├── clean.sh
├── test-qemu.sh
├── scripts/
├── configs/
├── assets/
├── archiso/
├── packages/
├── calamares/
├── docs/
└── .vscode/
```

## Uso rapido

Clonar y abrir en VS Code:

```bash
git clone REPOSITORIO
cd zentrix-os
code .
```

Construir ISO:

```bash
./build.sh
```

Salida esperada:

```text
out/zentrix-by-abraham-tobal-1.0-x86_64.iso
```

Limpiar artefactos:

```bash
./clean.sh
```

Probar en QEMU:

```bash
./test-qemu.sh
```

Probar instalacion completa en disco virtual:

```bash
./test-qemu.sh --install
```

Sincronizar logo oficial en todas las variantes:

```bash
./scripts/sync-brand-assets.sh
```

Sincronizar logos y wallpapers dentro del perfil staged de build:

```bash
./scripts/sync-live-assets.sh "$(pwd)" ./.build/profile
```

Probar la plataforma Zentrix hoy mismo sin instalar daemon del sistema:

```bash
cd zentrix-platform
python3 cli/main.py --local status
python3 cli/main.py --local profile list
python3 cli/main.py --local profile apply performance --dry-run
python3 gui/control_center.py --local
```

Si quieres usar la GUI o el daemon completo en desarrollo, instala antes las dependencias Python de la plataforma:

```bash
cd zentrix-platform
python3 -m pip install -e .
```

## Como construye `build.sh`

1. Verifica sistema compatible y dependencias.
2. Copia el perfil base `releng` desde Archiso a un directorio temporal (`.build/profile`).
3. Aplica los overrides de `archiso/`.
4. Fusiona paquetes base + paquetes propios definidos en `packages/zentrix-extra.x86_64`.
5. Ejecuta `mkarchiso` para generar la ISO final.
6. Copia/normaliza la ultima ISO al nombre objetivo del proyecto.

Este enfoque evita romper componentes criticos de arranque y mantiene una base estable de Arch Linux.

## Baseline Fase 2 implementado

- Identidad de sistema en `os-release` para el entorno Live.
- Script `customize_airootfs.sh` para personalizacion durante build.
- Usuario live temporal `zentrix` (sin contrasena hardcodeada).
- Servicios habilitados de forma condicional si existen: NetworkManager y bluetooth.
- Autologin en TTY1 para el usuario live.
- Acceso directo de escritorio: Install Zentrix.
- Entradas de menu iniciales: Zentrix Welcome, Zentrix System Info, Zentrix Update.

## Avance Fase 3

- Build incluye paso de branding de menu de arranque para perfiles BIOS/UEFI comunes.
- Script dedicado: `scripts/brand-boot-menu.sh`.
- Integracion previa a `mkarchiso` en `build.sh`.

## Avance Fase 4

- Inicio automatico de KDE Plasma desde login live en tty1.
- Tema oscuro por defecto y ajustes visuales base de escritorio.
- Konsole con perfil "Zentrix Terminal".
- Script de primer inicio para aplicar wallpaper y look-and-feel.
- Sincronizacion automatica de logos y wallpapers al perfil staged durante el build.

## Avance Fase 5

- Configuracion live de SDDM en /etc/sddm.conf.d/zentrix-live.conf.
- Autologin del usuario temporal zentrix en Plasma.
- Habilitacion condicional de sddm.service en customize_airootfs.
- Deshabilitacion condicional de getty@tty1 para evitar conflicto con el display manager.

## Experiencia Live facil de instalar

- Al iniciar la sesion Live, aparece un dialogo simple con dos opciones: Try Zentrix o Install Zentrix.
- Si se elige Install Zentrix, se abre Calamares directamente.
- El escritorio mantiene acceso directo grande Install Zentrix.
- Existe regla polkit solo para el usuario live zentrix para evitar friccion en el arranque del instalador.

## Avance Fase 6

- Tema SDDM propio "zentrix" aplicado por defecto en Live.
- Pantalla de login oscura con logo oficial, reloj y controles de energia.
- Identidad visible: "Zentrix" y "by Abraham Tobal" en login.

## Avance Fase 7

- Tema Plymouth propio con estilo oscuro y mensaje de inicio Zentrix.
- Base de tema GRUB con identidad visual y timeout razonable.
- Script de soporte para aplicar tema GRUB en sistemas donde corresponda.
- Build sincroniza assets de boot (logos y fondo) automaticamente.

## Avance Fase 8

- Zentrix Welcome en GUI real con Python + PySide6.
- Boton principal "Install Zentrix" dentro de Welcome.
- zentrix-update con validaciones y elevacion segura.
- zentrix-info con modo `--fastfetch` y conteo de paquetes.
- Lanzadores de menu propios para Welcome, System Info y Update.

## Avance Fase 9

- Calamares configurado con branding `zentrix` y nombre de producto propio.
- Configuracion base de secuencia de instalacion para flujo simple.
- Recursos visuales de branding para instalador (logo + tema oscuro).
- Lanzador `zentrix-install` reforzado con validaciones.

## Avance Fase 10

- `build.sh` prepara nombre final esperado: `out/zentrix-by-abraham-tobal-1.0-x86_64.iso`.
- `test-qemu.sh` incluye modo `--install` con disco virtual para prueba de Calamares.
- Checklist completo de validacion en `docs/PHASE10.md`.

## Prueba con QEMU

`test-qemu.sh` detecta automaticamente la ISO mas reciente en `out/` y la arranca con parametros razonables para pruebas de Live ISO.

## Seguridad y buenas practicas

- No se incluyen contrasenas, tokens ni claves privadas.
- No se desactivan firmas de paquetes de pacman.
- No se habilita root sin contrasena.
- `clean.sh` solo elimina `work/`, `out/` y `.build/` dentro del repositorio.

## Proximos pasos

Consulta `docs/ROADMAP.md` para el plan por fases y `docs/BRANDING.md` para assets pendientes.
