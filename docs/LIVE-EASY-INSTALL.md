# Live Easy Install Flow

Objetivo: que la ISO Live se sienta simple de instalar, estilo flujo guiado.

## Comportamiento
1. Arranque de la ISO.
2. Login automatico del usuario live zinarix via SDDM.
3. KDE Plasma abre y muestra un dialogo inicial:
   - Try Zinarix
   - Install Zinarix
4. Si el usuario elige instalar, se ejecuta Calamares con zinarix-install.

## Archivos clave
- archiso/airootfs/usr/local/bin/zinarix-live-start
- archiso/airootfs/etc/skel/.config/autostart/zinarix-live-start.desktop
- archiso/airootfs/usr/local/bin/zinarix-install
- archiso/airootfs/etc/skel/Desktop/Install Zinarix.desktop
- archiso/airootfs/etc/polkit-1/rules.d/49-zinarix-calamares.rules

## Seguridad
- No se almacena ninguna contrasena.
- La regla polkit aplica solo al usuario live zinarix para lanzar /usr/bin/calamares.
- El sistema instalado sigue usando el flujo normal de usuarios en Calamares.
