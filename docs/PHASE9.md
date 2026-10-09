# Fase 9 - Integracion Calamares

Objetivo: integrar Calamares con identidad Zinarix y flujo de instalacion claro.

## Implementado
- Configuracion principal de Calamares en /etc/calamares/settings.conf.
- Branding activo: `zinarix`.
- Secuencia de pantallas orientada a instalacion simple:
  - Bienvenida
  - Idioma
  - Teclado
  - Particiones
  - Usuario
  - Resumen
  - Instalacion
  - Terminado
- Recursos de branding propios para Calamares:
  - Nombre del producto Zinarix by Abraham Tobal
  - Nombre corto Zinarix
  - Bootloader entry name Zinarix
  - Logo oficial Zinarix
  - Tema visual oscuro
- Lanzador `zinarix-install` con validaciones y manejo de privilegios.

## Archivos clave
- archiso/airootfs/etc/calamares/settings.conf
- archiso/airootfs/usr/share/calamares/branding/zinarix/branding.desc
- archiso/airootfs/usr/share/calamares/branding/zinarix/stylesheet.qss
- archiso/airootfs/usr/local/bin/zinarix-install

## Estado
Fase 9 implementada en perfil. Pendiente validacion completa en ISO real y ajuste fino de modulos segun version exacta de Calamares del host.
