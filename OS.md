📁OS
├── 📁src
│   ├── 📁KabotSatKernel          # your existing kernel tree (not shown for security)
│   └── 📁KabotSatOS
│       ├── 📁build               # build output: final images, kernel+rootfs bundles
│       │   └── .gitkeep
│       ├── 📁config               # OS configuration (buildroot/defconfig, busybox config, etc.)
│       │   ├── buildroot_defconfig
│       │   ├── busybox.config
│       │   └── fstab
│       ├── 📁scripts              # helper scripts for image creation, flashing, testing
│       │   ├── build_image.sh
│       │   ├── create_initramfs.sh
│       │   └── setup_sd_card.sh
│       ├── 📁rootfs               # user‑space root filesystem overlay
│       │   ├── 📁bin              # essential binaries (e.g., BusyBox symlinks)
│       │   ├── 📁sbin             # system binaries (init, poweroff, etc.)
│       │   │   └── init           # the PID 1 init script
│       │   ├── 📁dev              # static device nodes (if not using devtmpfs)
│       │   │   ├── console
│       │   │   └── null
│       │   ├── 📁etc              # configuration files
│       │   │   ├── inittab
│       │   │   ├── passwd
│       │   │   └── hostname
│       │   ├── 📁lib              # shared libraries (musl/glibc)
│       │   ├── 📁proc             # mount point for procfs
│       │   ├── 📁sys              # mount point for sysfs
│       │   ├── 📁tmp              # temporary files (tmpfs mount)
│       │   ├── 📁mnt              # generic mount point
│       │   └── 📁home             # optional user space
│       ├── 📁tools                # cross‑compiled user programs for the cubesat
│       │   └── .gitkeep
│       ├── 📁docs                 # OS documentation, architecture notes
│       │   └── design.md
│       ├── Makefile               # top‑level build orchestration
│       ├── README.md
│       └── .gitignore