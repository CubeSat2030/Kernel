# KabotSat Alpha cubesat

## Folder structure

Below is a **complete, exhaustive folder structure** for building a custom OS from scratch for a 32‑bit Raspberry Pi‑based cubesat (KabotSat Alpha). It includes all directories, subdirectories, and key files with brief descriptions of their purpose. This structure is designed to be self‑contained, reproducible, and ready for cross‑compilation.

```
KabotSatFirmware/                                         # directory
├── Makefile                                         # file
│
├── build/                                           # directory (build artifacts – ignored by git)
│
├── src/                                             # directory
│   ├── kernel/                                      # directory
│   │   └── linux-raspberrypi/                      # directory (Linux kernel submodule)
│   │       ├── Documentation/                      # directory
│   │       ├── Kbuild                               # file
│   │       ├── Kconfig                              # file
│   │       ├── MAINTAINERS                          # file
│   │       ├── Makefile                             # file
│   │       ├── README                               # file
│   │       ├── arch/                                # directory
│   │       │   ├── Kconfig                          # file
│   │       │   ├── arm/                            # directory
│   │       │   │   ├── Kconfig                      # file
│   │       │   │   ├── Kconfig.debug                # file
│   │       │   │   ├── Makefile                     # file
│   │       │   │   ├── boot/                       # directory
│   │       │   │   │   ├── Makefile                 # file
│   │       │   │   │   ├── dts/                    # directory
│   │       │   │   │   └── ...                     # (many files)
│   │       │   │   ├── common/                     # directory
│   │       │   │   ├── configs/                    # directory
│   │       │   │   ├── crypto/                     # directory
│   │       │   │   ├── include/                    # directory
│   │       │   │   ├── kernel/                     # directory
│   │       │   │   ├── lib/                        # directory
│   │       │   │   ├── mach-bcm/                   # directory
│   │       │   │   ├── mm/                         # directory
│   │       │   │   ├── net/                        # directory
│   │       │   │   ├── tools/                      # directory
│   │       │   │   └── xchg/                       # directory
│   │       │   └── ...                             # other architectures
│   │       ├── block/                              # directory
│   │       ├── crypto/                             # directory
│   │       ├── drivers/                            # directory
│   │       │   ├── Kconfig                         # file
│   │       │   ├── Makefile                        # file
│   │       │   ├── gpio/                           # directory
│   │       │   ├── i2c/                            # directory
│   │       │   ├── spi/                            # directory
│   │       │   ├── usb/                            # directory
│   │       │   └── ...                             # many other driver subdirectories
│   │       ├── firmware/                           # directory
│   │       ├── fs/                                 # directory
│   │       ├── include/                            # directory
│   │       ├── init/                               # directory
│   │       ├── ipc/                                # directory
│   │       ├── kernel/                             # directory
│   │       ├── lib/                                # directory
│   │       ├── mm/                                 # directory
│   │       ├── net/                                # directory
│   │       ├── samples/                            # directory
│   │       ├── scripts/                            # directory
│   │       ├── security/                           # directory
│   │       ├── sound/                              # directory
│   │       ├── tools/                              # directory
│   │       ├── usr/                                # directory
│   │       └── virt/                               # directory
│   │
│   ├── bootloader/                                 # directory
│   │   └── u-boot/                                 # directory (U‑Boot submodule)
│   │       ├── Kbuild                              # file
│   │       ├── Kconfig                             # file
│   │       ├── MAINTAINERS                         # file
│   │       ├── Makefile                            # file
│   │       ├── README                              # file
│   │       ├── arch/                               # directory
│   │       │   ├── Kconfig                         # file
│   │       │   ├── arm/                            # directory
│   │       │   │   ├── Kconfig                     # file
│   │       │   │   ├── Makefile                    # file
│   │       │   │   ├── config.mk                   # file
│   │       │   │   ├── cpu/                       # directory
│   │       │   │   ├── dts/                       # directory
│   │       │   │   ├── include/                   # directory
│   │       │   │   ├── lib/                       # directory
│   │       │   │   ├── mach-bcm/                  # directory
│   │       │   │   └── ...                        # other subdirectories
│   │       │   └── ...                            # other architectures
│   │       ├── board/                             # directory
│   │       ├── cmd/                               # directory
│   │       ├── common/                            # directory
│   │       ├── configs/                           # directory
│   │       ├── doc/                               # directory
│   │       ├── drivers/                           # directory
│   │       ├── dts/                               # directory
│   │       ├── env/                               # directory
│   │       ├── fs/                                # directory
│   │       ├── include/                           # directory
│   │       ├── lib/                               # directory
│   │       ├── net/                               # directory
│   │       ├── post/                              # directory
│   │       ├── scripts/                           # directory
│   │       ├── test/                              # directory
│   │       ├── tools/                             # directory
│   │       └── ...                                # other top-level files
│   │
│   ├── busybox/                                    # directory
│   │   └── busybox/                                # directory (Busybox submodule)
│   │       ├── Config.in                           # file
│   │       ├── Makefile                            # file
│   │       ├── Makefile.flags                      # file
│   │       ├── Makefile.help                       # file
│   │       ├── README                              # file
│   │       ├── applets/                            # directory
│   │       ├── arch/                               # directory
│   │       ├── archival/                           # directory
│   │       ├── coreutils/                          # directory
│   │       ├── debian/                             # directory
│   │       ├── docs/                               # directory
│   │       ├── editors/                            # directory
│   │       ├── examples/                           # directory
│   │       ├── findutils/                          # directory
│   │       ├── include/                            # directory
│   │       ├── init/                               # directory
│   │       ├── libbb/                              # directory
│   │       ├── libpwdgrp/                          # directory
│   │       ├── loginutils/                         # directory
│   │       ├── mailutils/                          # directory
│   │       ├── miscutils/                          # directory
│   │       ├── modutils/                           # directory
│   │       ├── networking/                         # directory
│   │       ├── printutils/                         # directory
│   │       ├── procps/                             # directory
│   │       ├── runit/                              # directory
│   │       ├── selinux/                            # directory
│   │       ├── shell/                              # directory
│   │       ├── sysklogd/                           # directory
│   │       ├── testsuite/                          # directory
│   │       └── util-linux/                         # directory
│   │
│   ├── init/                                       # directory
│   │   ├── init.c                                  # file
│   │   └── Makefile                                # file
│   │
│   ├── libs/                                       # directory
│   │   └── libkabot/                               # directory
│   │       ├── include/                            # directory
│   │       │   └── kabot.h                         # file
│   │       ├── src/                                # directory
│   │       │   └── kabot.c                         # file
│   │       └── Makefile                            # file
│   │
│   └── apps/                                       # directory
│       ├── telemetry/                              # directory
│       │   ├── main.c                              # file
│       │   ├── telemetry.h                         # file
│       │   └── Makefile                            # file
│       ├── attitude_control/                       # directory
│       │   ├── main.c                              # file
│       │   ├── pid.h                               # file
│       │   ├── pid.c                               # file
│       │   └── Makefile                            # file
│       ├── power_monitor/                          # directory
│       │   ├── main.c                              # file
│       │   └── Makefile                            # file
│       └── watchdog/                               # directory
│           ├── main.c                              # file
│           └── Makefile                            # file
│
├── configs/                                        # directory
│   ├── kernel.config                               # file
│   ├── busybox.config                              # file
│   ├── uboot.config                                # file
│   ├── device_tree/                                # directory
│   │   ├── bcm2708-rpi-zero-w.dts                  # file
│   │   ├── bcm2709-rpi-2-b.dts                     # file
│   │   └── kabotsat-overlay.dts                    # file
│   └── firmware/                                   # directory
│       ├── config.txt                              # file
│       └── cmdline.txt                             # file
│
├── overlays/                                       # directory
│   └── kabotsat-overlay.dtbo                       # file
│
├── patches/                                        # directory
│   ├── kernel/                                     # directory
│   │   └── 0001-custom-gpio-driver.patch           # file
│   ├── bootloader/                                 # directory
│   │   └── 0001-custom-env.patch                   # file
│   └── busybox/                                    # directory
│       └── 0001-custom-applet.patch                # file
│
├── rootfs_overlay/                                 # directory
│   ├── etc/                                        # directory
│   │   ├── inittab                                 # file
│   │   ├── fstab                                   # file
│   │   ├── profile                                 # file
│   │   ├── passwd                                  # file
│   │   ├── shadow                                  # file
│   │   ├── group                                   # file
│   │   ├── hostname                                # file
│   │   ├── hosts                                   # file
│   │   ├── network/                                # directory
│   │   │   └── interfaces                          # file
│   │   └── init.d/                                 # directory
│   │       ├── rcS                                 # file
│   │       ├── S01syslogd                          # file
│   │       ├── S02watchdog                         # file
│   │       ├── S03telemetry                        # file
│   │       └── S04attitude_control                 # file
│   ├── root/                                       # directory
│   │   └── .profile                                # file
│   └── usr/local/bin/                              # directory
│       ├── reset_system.sh                         # file
│       └── deploy_apps.sh                          # file
│
├── scripts/                                        # directory
│   ├── build_kernel.sh                             # file
│   ├── build_bootloader.sh                         # file
│   ├── build_busybox.sh                            # file
│   ├── build_rootfs.sh                             # file
│   ├── create_image.sh                             # file
│   ├── flash_sd.sh                                 # file
│   ├── apply_patches.sh                            # file
│   └── emulate_qemu.sh                             # file
│
├── tools/                                          # directory
│   └── toolchain/                                  # directory (optional, pre‑built cross‑compiler)
│
└── docs/                                           # directory
    ├── architecture/                               # directory
    ├── operations/                                 # directory
    └── hardware/                                   # directory
```

### Important File Contents (Brief Descriptions)

- **`.gitignore`** – Ignore `build/`, `tools/toolchain/`, `*.o`, `*.img`, etc.
- **`Makefile`** – Calls scripts in order:  
  `all: kernel bootloader rootfs image`  
  `clean: rm -rf build/`
- **`configs/kernel.config`** – Derived from `make ARCH=arm bcmrpi_defconfig` and customised for cubesat (enable I2C, SPI, PREEMPT_RT, etc.)
- **`configs/config.txt`** – Bootloader parameters:  
  ```
  arm_64bit=0
  kernel=zImage
  device_tree=bcm2708-rpi-zero-w.dtb
  dtoverlay=kabotsat-overlay
  enable_uart=1
  gpu_mem=16
  ```
- **`configs/cmdline.txt`** – Kernel boot arguments:  
  `console=tty1 console=ttyAMA0,115200 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait`
- **`rootfs_overlay/etc/inittab`** – Busybox init:  
  ```
  ::sysinit:/etc/init.d/rcS
  ::respawn:-/bin/sh
  ttyAMA0::respawn:/sbin/getty -L ttyAMA0 115200 vt100
  ```
- **`rootfs_overlay/etc/init.d/rcS`** – Startup script that runs all `S??*` scripts.
- **`scripts/build_kernel.sh`** – Example steps:
  ```bash
  cd src/kernel/linux-raspberrypi
  make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- O=../../../build/kernel KCONFIG_CONFIG=../../../configs/kernel.config olddefconfig
  make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- O=../../../build/kernel -j$(nproc) zImage modules dtbs
  make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- O=../../../build/kernel modules_install INSTALL_MOD_PATH=../../../build/rootfs
  cp build/kernel/arch/arm/boot/zImage build/boot/
  cp build/kernel/arch/arm/boot/dts/*.dtb build/boot/
  ```
- **`scripts/create_image.sh`** – Creates a partitioned image (using `dd` and `fdisk`), formats partitions (FAT32, ext4), mounts them, copies boot files and rootfs.
