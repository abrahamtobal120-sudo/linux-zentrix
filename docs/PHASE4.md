# Fase 4 - Integracion KDE Plasma

Objetivo: lograr una experiencia Live KDE moderna y funcional sin comprometer estabilidad.

## Implementado
- Arranque automatico de Plasma desde tty1 para usuario live.
- Tema oscuro por defecto (Breeze Dark) y ajustes visuales base.
- Perfil de Konsole renombrado a Zentrix Terminal.
- Script de primer inicio KDE para aplicar wallpaper y look-and-feel.
- Sincronizacion automatica de logos y wallpapers al perfil de build.
- Paquetes KDE de integracion de red y portal agregados.

## Archivos clave
- archiso/airootfs/etc/skel/.bash_profile
- archiso/airootfs/etc/skel/.config/kdeglobals
- archiso/airootfs/etc/skel/.config/kwinrc
- archiso/airootfs/etc/skel/.config/konsolerc
- archiso/airootfs/etc/skel/.local/share/konsole/Zentrix.profile
- archiso/airootfs/usr/local/bin/zentrix-apply-kde-defaults
- scripts/sync-live-assets.sh

## Resultado esperado
Al iniciar la ISO en modo Live:
- Login automatico del usuario zentrix en tty1.
- Inicio de KDE Plasma.
- Aplicacion de defaults visuales de Zentrix en primer login.
- Wallpaper por defecto disponible en /usr/share/wallpapers/zentrix-dark.png.
