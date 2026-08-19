# Fase 7 - Plymouth y GRUB

Objetivo: aplicar identidad Zentrix en arranque visual y dejar base de tema GRUB mantenible.

## Implementado
- Tema Plymouth personalizado `zentrix` con layout minimalista oscuro.
- Mensaje visual de arranque: ZENTRIX / by Abraham Tobal / Starting...
- Configuracion de daemon Plymouth en /etc/plymouth/plymouthd.conf.
- Tema GRUB base en /usr/share/grub/themes/zentrix/theme.txt.
- Defaults de GRUB para distribuidor Zentrix y timeout razonable.
- Script utilitario zentrix-apply-grub-theme para regenerar grub.cfg cuando aplique.
- Sincronizacion automatica de assets de boot (logo/fondo) en el pipeline de build.

## Archivos clave
- archiso/airootfs/usr/share/plymouth/themes/zentrix/zentrix.plymouth
- archiso/airootfs/usr/share/plymouth/themes/zentrix/zentrix.script
- archiso/airootfs/etc/plymouth/plymouthd.conf
- archiso/airootfs/usr/share/grub/themes/zentrix/theme.txt
- archiso/airootfs/etc/default/grub.d/zentrix.cfg
- archiso/airootfs/usr/local/bin/zentrix-apply-grub-theme
- scripts/sync-live-assets.sh

## Estado
Fase 7 implementada en perfil. Pendiente validacion visual en ISO real.
