# Fase 10 - Validacion completa de instalacion

Objetivo: validar de extremo a extremo el flujo Live + instalacion + primer arranque del sistema instalado.

## Preparacion
1. Instalar dependencias en host Arch:
   sudo pacman -S --needed archiso qemu-full rsync git
2. Construir ISO:
   ./build.sh
3. Confirmar salida esperada:
   out/zinarix-by-abraham-tobal-1.0-x86_64.iso

## Pruebas recomendadas

### A. Prueba Live rapida
- Ejecutar: ./test-qemu.sh
- Verificar:
  - Menu de arranque con identidad Zinarix.
  - Login SDDM con tema Zinarix.
  - Apertura de Zinarix Welcome.
  - Opcion Install Zinarix disponible.

### B. Prueba de instalacion en disco virtual
- Ejecutar: ./test-qemu.sh --install
- Verificar en Calamares:
  - Branding: Zinarix by Abraham Tobal.
  - Flujo de pantallas:
    - Bienvenida
    - Idioma
    - Teclado
    - Particiones
    - Usuario
    - Resumen
    - Instalacion
    - Terminado

### C. Primer arranque post-instalacion
- Reiniciar VM desde disco virtual.
- Verificar:
  - GRUB con tema Zinarix.
  - Plymouth con tema Zinarix.
  - SDDM con tema Zinarix.
  - KDE Plasma funcional.
  - Comandos:
    - zinarix-info
    - zinarix-update
    - zinarix-welcome

## Resultado esperado
- ISO instalable y utilizable como sistema propio Zinarix.
- Archivo final disponible en:
  out/zinarix-by-abraham-tobal-1.0-x86_64.iso

## Nota
En este entorno de desarrollo, si no existe mkarchiso, la validacion completa queda pendiente hasta ejecutar en un host Arch con archiso instalado.
