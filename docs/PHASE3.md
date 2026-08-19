# Fase 3 - ISO minima que arranque

Objetivo: asegurar que la ISO Zentrix arranque en BIOS y UEFI con menu de identidad propia.

## Implementado
- Pipeline de build con paso de branding de menu de arranque.
- Script: scripts/brand-boot-menu.sh
- Integracion en build.sh antes de mkarchiso.
- Reglas de reemplazo no destructivas para archivos de boot comunes de Archiso.

## Resultado esperado al compilar
- Entrada principal: Try Zentrix
- Entrada secundaria: Advanced options
- Titulo de menu: ZENTRIX

## Nota
La entrada dedicada "Install Zentrix" se completara cuando se cierre la integracion de Calamares y flujo de instalacion (Fase 9), para evitar entradas de arranque enganosas antes de validar el instalador.
