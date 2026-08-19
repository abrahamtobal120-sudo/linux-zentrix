#!/usr/bin/env bash

iso_name="zentrix-by-abraham-tobal"
iso_label="ZENTRIX_1_0"
iso_publisher="Abraham Tobal <https://example.com>"
iso_application="Zentrix by Abraham Tobal Live/Rescue CD"
iso_version="1.0"
install_dir="zentrix"
buildmodes=("iso")
bootmodes=(
  "bios.syslinux.mbr"
  "bios.syslinux.eltorito"
  "uefi-x64.systemd-boot.esp"
  "uefi-x64.systemd-boot.eltorito"
)
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=("-comp" "xz" "-Xbcj" "x86")
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/customize_airootfs.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/zentrix-info"]="0:0:755"
  ["/usr/local/bin/zentrix-update"]="0:0:755"
  ["/usr/local/bin/zentrix-welcome"]="0:0:755"
  ["/usr/local/bin/zentrixctl"]="0:0:755"
  ["/usr/local/bin/zentrix-control-center"]="0:0:755"
  ["/usr/local/bin/zentrix-profiles"]="0:0:755"
  ["/usr/local/bin/zentrix-driver-center"]="0:0:755"
  ["/usr/local/bin/zentrix-app-center"]="0:0:755"
  ["/usr/local/bin/zentrix-recovery"]="0:0:755"
  ["/usr/local/bin/zentrix-parental-control"]="0:0:755"
  ["/usr/local/bin/zentrix-first-setup"]="0:0:755"
  ["/usr/local/bin/zentrix-first-setup-launcher"]="0:0:755"
  ["/usr/local/bin/zentrix-target-prep"]="0:0:755"
  ["/usr/local/bin/zentrix-apply-kde-defaults"]="0:0:755"
  ["/usr/local/bin/zentrix-install"]="0:0:755"
  ["/usr/local/bin/zentrix-live-start"]="0:0:755"
  ["/usr/local/bin/zentrix-apply-grub-theme"]="0:0:755"
)
