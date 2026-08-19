# Fase 10 - Validacion completa de instalacion

Objetivo: validar de extremo a extremo el flujo Live + instalacion + primer arranque del sistema instalado.

## Preparacion
1. Instalar dependencias en host Arch:
   sudo pacman -S --needed archiso qemu-full rsync git
2. Construir ISO:
   ./build.sh
3. Confirmar salida esperada:
   out/zentrix-by-abraham-tobal-1.0-x86_64.iso

## Pruebas recomendadas

### A. Prueba Live rapida
- Ejecutar: ./test-qemu.sh
- Verificar:
  - Menu de arranque con identidad Zentrix.
  - Login SDDM con tema Zentrix.
  - Apertura de Zentrix Welcome.
  - Opcion Install Zentrix disponible.

### B. Prueba de instalacion en disco virtual
- Ejecutar: ./test-qemu.sh --install
- Verificar en Calamares:
  - Branding: Zentrix by Abraham Tobal.
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
  - GRUB con tema Zentrix.
  - Plymouth con tema Zentrix.
  - SDDM con tema Zentrix.
  - KDE Plasma funcional.
  - Comandos:
    - zentrix-info
    - zentrix-update
    - zentrix-welcome

## Resultado esperado
- ISO instalable y utilizable como sistema propio Zentrix.
- Archivo final disponible en:
  out/zentrix-by-abraham-tobal-1.0-x86_64.iso

## Nota
En este entorno de desarrollo, si no existe mkarchiso, la validacion completa queda pendiente hasta ejecutar en un host Arch con archiso instalado.
