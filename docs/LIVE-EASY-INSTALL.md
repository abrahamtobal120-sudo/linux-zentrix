# Live Easy Install Flow

Objetivo: que la ISO Live se sienta simple de instalar, estilo flujo guiado.

## Comportamiento
1. Arranque de la ISO.
2. Login automatico del usuario live zentrix via SDDM.
3. KDE Plasma abre y muestra un dialogo inicial:
   - Try Zentrix
   - Install Zentrix
4. Si el usuario elige instalar, se ejecuta Calamares con zentrix-install.

## Archivos clave
- archiso/airootfs/usr/local/bin/zentrix-live-start
- archiso/airootfs/etc/skel/.config/autostart/zentrix-live-start.desktop
- archiso/airootfs/usr/local/bin/zentrix-install
- archiso/airootfs/etc/skel/Desktop/Install Zentrix.desktop
- archiso/airootfs/etc/polkit-1/rules.d/49-zentrix-calamares.rules

## Seguridad
- No se almacena ninguna contrasena.
- La regla polkit aplica solo al usuario live zentrix para lanzar /usr/bin/calamares.
- El sistema instalado sigue usando el flujo normal de usuarios en Calamares.
