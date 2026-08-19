# Fase 8 - Aplicaciones Zentrix

Objetivo: ofrecer aplicaciones propias iniciales para una experiencia Zentrix mas guiada y profesional.

## Implementado
- Zentrix Welcome en GUI real con Python + PySide6.
- Acciones rapidas: internet, update, install, apariencia, system info.
- Boton principal Install Zentrix dentro de Welcome.
- zentrix-update reforzado con validaciones y elevacion segura.
- zentrix-info mejorado con conteo de paquetes y modo --fastfetch.
- Lanzadores .desktop actualizados para flujo de usuario.

## Archivos clave
- archiso/airootfs/usr/local/lib/zentrix/zentrix_welcome.py
- archiso/airootfs/usr/local/bin/zentrix-welcome
- archiso/airootfs/usr/local/bin/zentrix-update
- archiso/airootfs/usr/local/bin/zentrix-info
- archiso/airootfs/usr/share/applications/zentrix-welcome.desktop
- archiso/airootfs/usr/share/applications/zentrix-system-info.desktop
- archiso/airootfs/usr/share/applications/zentrix-update.desktop

## Estado
Fase 8 implementada en perfil. Pendiente validacion de UX en ISO real.
