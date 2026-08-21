LABEL zentrix
TEXT HELP
Start Zentrix Live.
You can explore Zentrix and install it from the desktop.
ENDTEXT
MENU LABEL ^Zentrix Live
LINUX /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux
INITRD /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux.img
APPEND archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID%

LABEL zentrixguest
TEXT HELP
Start Zentrix in Guest Mode.
Guest has no administrator privileges and its session is temporary.
ENDTEXT
MENU LABEL Zentrix ^Guest Mode
LINUX /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux
INITRD /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux.img
APPEND archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% zentrix_guest=1

LABEL zentrixspeech
TEXT HELP
Start Zentrix with accessibility screen reader enabled.
ENDTEXT
MENU LABEL Zentrix Live with ^speech
LINUX /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux
INITRD /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux.img
APPEND archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% accessibility=on0o

