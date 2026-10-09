#!/usr/bin/env bash

iso_name="zinarix-by-abraham-tobal"
iso_label="ZINARIX_1_0"
iso_publisher="Abraham Tobal <https://example.com>"
iso_application="Zinarix by Abraham Tobal Live/Rescue CD"
iso_version="1.0"
install_dir="zinarix"
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
  ["/etc/sudoers.d/49-zinarix-calamares"]="0:0:440"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/customize_airootfs.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/zinarix-info"]="0:0:755"
  ["/usr/local/bin/zinarix-update"]="0:0:755"
  ["/usr/local/bin/zinarix-welcome"]="0:0:755"
  ["/usr/local/bin/zinarixctl"]="0:0:755"
  ["/usr/local/bin/zinarix-control-center"]="0:0:755"
  ["/usr/local/bin/zinarix-profiles"]="0:0:755"
  ["/usr/local/bin/zinarix-driver-center"]="0:0:755"
  ["/usr/local/bin/zinarix-app-center"]="0:0:755"
  ["/usr/local/bin/zinarix-recovery"]="0:0:755"
  ["/usr/local/bin/zinarix-first-setup"]="0:0:755"
  ["/usr/local/bin/zinarix-first-setup-launcher"]="0:0:755"
  ["/usr/local/bin/zinarix-target-prep"]="0:0:755"
  ["/usr/local/bin/zinarix-apply-kde-defaults"]="0:0:755"
  ["/usr/local/bin/zinarix-install"]="0:0:755"
  ["/usr/local/bin/zinarix-live-start"]="0:0:755"
  ["/usr/local/bin/zinarix-apply-grub-theme"]="0:0:755"
)
