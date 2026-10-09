# Fase 7 - Plymouth y GRUB

Objetivo: aplicar identidad Zinarix en arranque visual y dejar base de tema GRUB mantenible.

## Implementado
- Tema Plymouth personalizado `zinarix` con layout minimalista oscuro.
- Mensaje visual de arranque: ZINARIX / by Abraham Tobal / Starting...
- Configuracion de daemon Plymouth en /etc/plymouth/plymouthd.conf.
- Tema GRUB base en /usr/share/grub/themes/zinarix/theme.txt.
- Defaults de GRUB para distribuidor Zinarix y timeout razonable.
- Script utilitario zinarix-apply-grub-theme para regenerar grub.cfg cuando aplique.
- Sincronizacion automatica de assets de boot (logo/fondo) en el pipeline de build.

## Archivos clave
- archiso/airootfs/usr/share/plymouth/themes/zinarix/zinarix.plymouth
- archiso/airootfs/usr/share/plymouth/themes/zinarix/zinarix.script
- archiso/airootfs/etc/plymouth/plymouthd.conf
- archiso/airootfs/usr/share/grub/themes/zinarix/theme.txt
- archiso/airootfs/etc/default/grub.d/zinarix.cfg
- archiso/airootfs/usr/local/bin/zinarix-apply-grub-theme
- scripts/sync-live-assets.sh

## Estado
Fase 7 implementada en perfil. Pendiente validacion visual en ISO real.
