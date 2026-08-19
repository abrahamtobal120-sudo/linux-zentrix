# Fase 9 - Integracion Calamares

Objetivo: integrar Calamares con identidad Zentrix y flujo de instalacion claro.

## Implementado
- Configuracion principal de Calamares en /etc/calamares/settings.conf.
- Branding activo: `zentrix`.
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
  - Nombre del producto Zentrix by Abraham Tobal
  - Nombre corto Zentrix
  - Bootloader entry name Zentrix
  - Logo oficial Zentrix
  - Tema visual oscuro
- Lanzador `zentrix-install` con validaciones y manejo de privilegios.

## Archivos clave
- archiso/airootfs/etc/calamares/settings.conf
- archiso/airootfs/usr/share/calamares/branding/zentrix/branding.desc
- archiso/airootfs/usr/share/calamares/branding/zentrix/stylesheet.qss
- archiso/airootfs/usr/local/bin/zentrix-install

## Estado
Fase 9 implementada en perfil. Pendiente validacion completa en ISO real y ajuste fino de modulos segun version exacta de Calamares del host.
