#!/usr/bin/env python3

import json
import os
import re
import shutil
import subprocess
import threading
import tkinter as tk

from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext


# ============================================================
# CubeSat2030 KernelNanny
# Linux Kernel Subsystem Removal / Build Utility
# ============================================================

CONFIG_PATH = Path.home() / ".kernel_subsystem_remover_config.json"

DEFAULT_KERNEL_DIR = "../../linux"

BACKUP_ROOT = Path.home() / "KernelNanny_Backups"


# ============================================================
# SUBSYSTEM DEFINITIONS
# ============================================================
#
# IMPORTANT:
# These definitions deliberately avoid deleting entire
# high-level kernel subsystems such as drivers/gpu or
# drivers/media because doing so can remove dependencies
# required by other parts of the Raspberry Pi kernel.
#
# The objective is to remove the subsystem's normal build
# entry points and source trees where practical.
#
# Always use DRY RUN first.
# ============================================================

SUBSYSTEMS = {

    # --------------------------------------------------------
    # NETWORKING
    # --------------------------------------------------------
    "net": {
        "description": "Networking / TCP-IP / network drivers",

        "dirs": [
            "net",
            "drivers/net",
            "arch/arm/net",
        ],

        "files": [
            (
                "Kconfig",
                r'^source\s+"net/Kconfig"\s*$',
                '# source "net/Kconfig"',
            ),
            (
                "lib/Kconfig.debug",
                r'^source\s+"net/Kconfig.debug"\s*$',
                '# source "net/Kconfig.debug"',
            ),
            (
                "fs/Kconfig",
                r'^source\s+"net/sunrpc/Kconfig"\s*$',
                '# source "net/sunrpc/Kconfig"',
            ),
            (
                "Kbuild",
                r'^obj-\$\(CONFIG_NET\)\s*\+=\s*net/',
                '# obj-$(CONFIG_NET) += net/',
            ),
            (
                "drivers/Makefile",
                r'^obj-y\s*\+=\s*net/',
                '# obj-y += net/',
            ),
            (
                "drivers/Kconfig",
                r'^source\s+"drivers/net/Kconfig"\s*$',
                '# source "drivers/net/Kconfig"',
            ),
            (
                "arch/arm/Kbuild",
                r'^obj-y\s*\+=\s*net/',
                '# obj-y += net/',
            ),
        ],
    },


    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------
    "sound": {
        "description": "ALSA / sound / audio subsystem",

        "dirs": [
            "sound",
        ],

        "files": [
            (
                "Kbuild",
                r'^obj-y\s*\+=\s*sound/',
                '# obj-y += sound/',
            ),
            (
                "drivers/Kconfig",
                r'^source\s+"sound/Kconfig"\s*$',
                '# source "sound/Kconfig"',
            ),
            (
                "drivers/Makefile",
                r'^obj-\$\(CONFIG_SOUND\)\s*\+=\s*sound/',
                '# obj-$(CONFIG_SOUND) += sound/',
            ),
        ],
    },


    # --------------------------------------------------------
    # BLUETOOTH
    # --------------------------------------------------------
    "bluetooth": {
        "description": "Bluetooth core and Bluetooth drivers",

        "dirs": [
            "net/bluetooth",
            "drivers/bluetooth",
            "include/net/bluetooth",
        ],

        "files": [
            (
                "net/Kconfig",
                r'^source\s+"net/bluetooth/Kconfig"\s*$',
                '# source "net/bluetooth/Kconfig"',
            ),
            (
                "drivers/Kconfig",
                r'^source\s+"drivers/bluetooth/Kconfig"\s*$',
                '# source "drivers/bluetooth/Kconfig"',
            ),
            (
                "drivers/Makefile",
                r'^obj-\$\(CONFIG_BT\)\s*\+=\s*bluetooth/',
                '# obj-$(CONFIG_BT) += bluetooth/',
            ),
        ],
    },


    # --------------------------------------------------------
    # VIRTUALIZATION
    # --------------------------------------------------------
    "virt": {
        "description": "Kernel virtualization support",

        "dirs": [
            "virt",
        ],

        "files": [
            (
                "Kbuild",
                r'^obj-y\s*\+=\s*virt/',
                '# obj-y += virt/',
            ),
            (
                "drivers/Makefile",
                r'^obj-\$\(CONFIG_VIRT_DRIVERS\)\s*\+=\s*virt/',
                '# obj-$(CONFIG_VIRT_DRIVERS) += virt/',
            ),
            (
                "drivers/Kconfig",
                r'^source\s+"virt/lib/Kconfig"\s*$',
                '# source "virt/lib/Kconfig"',
            ),
        ],
    },


    # --------------------------------------------------------
    # VIDEO / GRAPHICS
    # --------------------------------------------------------
    #
    # We remove the conventional entry points rather than
    # blindly deleting drivers/gpu and drivers/video.
    #
    # This is much safer for Raspberry Pi kernels because
    # DRM, framebuffer, firmware and display components can
    # have cross-dependencies.
    # --------------------------------------------------------
    "video": {
        "description": "Video / framebuffer / DRM / display support",

        "dirs": [
            "drivers/video",
        ],

        "files": [
            (
                "drivers/Kconfig",
                r'^source\s+"drivers/video/Kconfig"\s*$',
                '# source "drivers/video/Kconfig"',
            ),
            (
                "drivers/Makefile",
                r'^obj-\$\(CONFIG_DRM\)\s*\+=\s*gpu/',
                '# obj-$(CONFIG_DRM) += gpu/',
            ),
            (
                "drivers/Kconfig",
                r'^source\s+"drivers/gpu/Kconfig"\s*$',
                '# source "drivers/gpu/Kconfig"',
            ),
            (
                "drivers/Kconfig",
                r'^source\s+"drivers/video/Kconfig"\s*$',
                '# source "drivers/video/Kconfig"',
            ),
        ],
    },


    # --------------------------------------------------------
    # HDMI / DISPLAY BRIDGE
    # --------------------------------------------------------
    #
    # HDMI normally lives inside the DRM subsystem. Therefore
    # HDMI is treated separately from generic graphics.
    #
    # We do NOT delete drivers/gpu.
    # --------------------------------------------------------
    "hdmi": {
        "description": "HDMI / display connector support",

        "dirs": [
            "drivers/gpu/drm/bridge",
        ],

        "files": [
            (
                "drivers/gpu/drm/Kconfig",
                r'^source\s+"drivers/gpu/drm/bridge/Kconfig"\s*$',
                '# source "drivers/gpu/drm/bridge/Kconfig"',
            ),
        ],
    },


    # --------------------------------------------------------
    # MEDIA / CAMERA
    # --------------------------------------------------------
    #
    # Useful for a spacecraft kernel where camera capture is
    # not required.
    # --------------------------------------------------------
    "media": {
        "description": "Video4Linux / camera / media subsystem",

        "dirs": [
            "drivers/media",
        ],

        "files": [
            (
                "drivers/Kconfig",
                r'^source\s+"drivers/media/Kconfig"\s*$',
                '# source "drivers/media/Kconfig"',
            ),
            (
                "drivers/Makefile",
                r'^obj-\$\(CONFIG_MEDIA_SUPPORT\)\s*\+=\s*media/',
                '# obj-$(CONFIG_MEDIA_SUPPORT) += media/',
            ),
        ],
    },
}


# ============================================================
# GUI APPLICATION
# ============================================================

class KernelNannyGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("CubeSat2030 KernelNanny")
        self.root.geometry("1000x720")
        self.root.minsize(850, 600)

        self.build_running = False

        # ----------------------------------------------------
        # Load configuration
        # ----------------------------------------------------

        self.config = self.load_config()

        # ----------------------------------------------------
        # Kernel directory
        # ----------------------------------------------------

        tk.Label(
            root,
            text="Kernel Source Directory:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=8,
            pady=8
        )

        self.kernel_dir_var = tk.StringVar(
            value=self.config.get(
                "kernel_dir",
                DEFAULT_KERNEL_DIR
            )
        )

        tk.Entry(
            root,
            textvariable=self.kernel_dir_var,
            width=75
        ).grid(
            row=0,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=8,
            pady=8
        )

        tk.Button(
            root,
            text="Browse",
            command=self.browse_kernel_dir
        ).grid(
            row=0,
            column=3,
            padx=8,
            pady=8
        )


        # ----------------------------------------------------
        # Dry run
        # ----------------------------------------------------

        self.dry_run_var = tk.BooleanVar(
            value=self.config.get("dry_run", True)
        )

        self.dry_run_check = tk.Checkbutton(
            root,
            text="Dry Run (recommended first)",
            variable=self.dry_run_var
        )

        self.dry_run_check.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            padx=20,
            pady=4
        )


        # ----------------------------------------------------
        # Automatic backup
        # ----------------------------------------------------

        self.backup_var = tk.BooleanVar(
            value=self.config.get("backup", True)
        )

        self.backup_check = tk.Checkbutton(
            root,
            text="Create backup before removal",
            variable=self.backup_var
        )

        self.backup_check.grid(
            row=1,
            column=2,
            columnspan=2,
            sticky="w",
            padx=20,
            pady=4
        )


        # ----------------------------------------------------
        # Subsystem section
        # ----------------------------------------------------

        tk.Label(
            root,
            text="Select subsystems to remove:",
            font=("TkDefaultFont", 10, "bold")
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=8,
            pady=(10, 5)
        )

        self.subsystem_vars = {}

        selected_subsystems = self.config.get(
            "selected_subsystems",
            []
        )

        row = 3

        for name, spec in SUBSYSTEMS.items():

            var = tk.BooleanVar(
                value=name in selected_subsystems
            )

            self.subsystem_vars[name] = var

            check = tk.Checkbutton(
                root,
                text=f"{name} — {spec['description']}",
                variable=var
            )

            check.grid(
                row=row,
                column=0,
                columnspan=4,
                sticky="w",
                padx=20,
                pady=2
            )

            row += 1


        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        button_row = row

        self.apply_btn = tk.Button(
            root,
            text="Apply Removals",
            command=self.apply_removals,
            bg="#f0a0a0",
            width=20
        )

        self.apply_btn.grid(
            row=button_row,
            column=0,
            padx=8,
            pady=12,
            sticky="w"
        )


        self.build_btn = tk.Button(
            root,
            text="Build Kernel",
            command=self.build_kernel,
            width=20
        )

        self.build_btn.grid(
            row=button_row,
            column=1,
            padx=8,
            pady=12,
            sticky="w"
        )


        self.clean_log_btn = tk.Button(
            root,
            text="Clear Log",
            command=self.clear_log,
            width=15
        )

        self.clean_log_btn.grid(
            row=button_row,
            column=2,
            padx=8,
            pady=12,
            sticky="w"
        )


        # ----------------------------------------------------
        # Log
        # ----------------------------------------------------

        self.log_text = scrolledtext.ScrolledText(
            root,
            width=110,
            height=25,
            state="normal",
            wrap=tk.WORD
        )

        self.log_text.grid(
            row=button_row + 1,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=8,
            pady=8
        )


        # ----------------------------------------------------
        # Grid expansion
        # ----------------------------------------------------

        root.columnconfigure(1, weight=1)

        root.rowconfigure(
            button_row + 1,
            weight=1
        )


        # ----------------------------------------------------
        # Welcome message
        # ----------------------------------------------------

        self.log(
            "\n"
            "========================================\n"
            " CubeSat2030 KernelNanny\n"
            " Linux Kernel Subsystem Manager\n"
            "========================================\n\n"
        )

        self.log(
            "Dry Run is ENABLED by default.\n"
            "Run a dry run before performing destructive removal.\n\n"
        )


    # ========================================================
    # CONFIGURATION
    # ========================================================

    def load_config(self):

        if CONFIG_PATH.exists():

            try:

                with open(
                    CONFIG_PATH,
                    "r",
                    encoding="utf-8"
                ) as f:

                    return json.load(f)

            except Exception:
                pass

        return {}


    def save_config(self):

        config = {

            "kernel_dir":
                self.kernel_dir_var.get(),

            "selected_subsystems": [
                name
                for name, var in self.subsystem_vars.items()
                if var.get()
            ],

            "dry_run":
                self.dry_run_var.get(),

            "backup":
                self.backup_var.get(),
        }

        try:

            with open(
                CONFIG_PATH,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    config,
                    f,
                    indent=2
                )

        except Exception as e:

            self.log(
                f"WARNING: Could not save configuration: {e}\n"
            )


    # ========================================================
    # THREAD-SAFE LOGGING
    # ========================================================

    def log(self, message):

        def write():

            self.log_text.insert(
                tk.END,
                message
            )

            self.log_text.see(tk.END)

        try:

            self.root.after(
                0,
                write
            )

        except Exception:
            pass


    def clear_log(self):

        self.log_text.delete(
            "1.0",
            tk.END
        )


    # ========================================================
    # DIRECTORY SELECTION
    # ========================================================

    def browse_kernel_dir(self):

        current = self.kernel_dir_var.get()

        try:
            initial_dir = str(
                Path(current).expanduser().resolve()
            )
        except Exception:
            initial_dir = str(Path.home())

        directory = filedialog.askdirectory(
            initialdir=initial_dir
        )

        if directory:

            self.kernel_dir_var.set(
                directory
            )


    # ========================================================
    # KERNEL VALIDATION
    # ========================================================

    def validate_kernel_directory(self, kernel_dir):

        if not kernel_dir.exists():

            return False, (
                "Kernel directory does not exist."
            )

        if not kernel_dir.is_dir():

            return False, (
                "Kernel path is not a directory."
            )

        required_files = [
            "Makefile",
            "Kconfig",
        ]

        missing = [
            f
            for f in required_files
            if not (kernel_dir / f).exists()
        ]

        if missing:

            return False, (
                "This does not appear to be a Linux kernel "
                f"source tree.\nMissing: {', '.join(missing)}"
            )

        return True, ""


    # ========================================================
    # BACKUP
    # ========================================================

    def create_backup(self, kernel_dir):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_dir = (
            BACKUP_ROOT /
            f"kernel_backup_{timestamp}"
        )

        self.log(
            "\nCreating kernel backup:\n"
            f"  Source: {kernel_dir}\n"
            f"  Backup: {backup_dir}\n\n"
        )

        try:

            BACKUP_ROOT.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copytree(
                kernel_dir,
                backup_dir
            )

            self.log(
                "Backup completed successfully.\n\n"
            )

            return backup_dir

        except Exception as e:

            self.log(
                f"ERROR: Backup failed: {e}\n"
            )

            return None


    # ========================================================
    # COMMENT KCONFIG/KBUILD LINE
    # ========================================================

    def comment_out_line(
        self,
        file_path,
        pattern,
        replacement,
        dry_run=False
    ):

        path = Path(file_path)

        if not path.exists():

            self.log(
                f"  File not found: {path}\n"
            )

            return


        try:

            text = path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            text = path.read_text(
                encoding="latin-1"
            )


        lines = text.splitlines()

        changed = False

        for i, line in enumerate(lines):

            stripped = line.strip()

            if (
                re.match(pattern, stripped)
                and not stripped.startswith("#")
            ):

                self.log(
                    f"  Match in {path}:\n"
                    f"    {line}\n"
                    f"    -> {replacement}\n"
                )

                if not dry_run:

                    lines[i] = replacement

                changed = True


        if changed and not dry_run:

            path.write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8"
            )

            self.log(
                f"  Updated: {path}\n"
            )

        elif not changed:

            self.log(
                f"  No active match in {path}\n"
            )


    # ========================================================
    # DELETE DIRECTORY
    # ========================================================

    def remove_directory(
        self,
        target,
        dry_run=False
    ):

        if not target.exists():

            self.log(
                f"  Already absent: {target}\n"
            )

            return


        if dry_run:

            self.log(
                f"  [DRY RUN] Would delete: {target}\n"
            )

            return


        try:

            if target.is_dir():

                shutil.rmtree(target)

            else:

                target.unlink()

            self.log(
                f"  Deleted: {target}\n"
            )

        except Exception as e:

            self.log(
                f"  ERROR deleting {target}: {e}\n"
            )


    # ========================================================
    # APPLY REMOVALS
    # ========================================================

    def apply_removals(self):

        if self.build_running:

            messagebox.showwarning(
                "Busy",
                "A kernel build is currently running."
            )

            return


        kernel_dir = Path(
            self.kernel_dir_var.get()
        ).expanduser()


        valid, error = self.validate_kernel_directory(
            kernel_dir
        )

        if not valid:

            messagebox.showerror(
                "Invalid Kernel Directory",
                error
            )

            return


        selected = [
            name
            for name, var
            in self.subsystem_vars.items()
            if var.get()
        ]


        if not selected:

            messagebox.showinfo(
                "Nothing selected",
                "Select at least one subsystem."
            )

            return


        dry_run = self.dry_run_var.get()


        # ----------------------------------------------------
        # Confirmation
        # ----------------------------------------------------

        if dry_run:

            message = (
                "Dry Run is enabled.\n\n"
                "No files will be deleted or modified.\n\n"
                "Selected:\n"
                + "\n".join(
                    f"  • {name}"
                    for name in selected
                )
                + "\n\nContinue?"
            )

        else:

            message = (
                "WARNING: This will modify the kernel source tree.\n\n"
                "Selected:\n"
                + "\n".join(
                    f"  • {name}"
                    for name in selected
                )
                + "\n\n"
                "A backup is strongly recommended.\n\n"
                "Continue?"
            )


        if not messagebox.askyesno(
            "Confirm Kernel Changes",
            message
        ):

            return


        self.save_config()


        # ----------------------------------------------------
        # Backup
        # ----------------------------------------------------

        if not dry_run and self.backup_var.get():

            backup = self.create_backup(
                kernel_dir
            )

            if backup is None:

                if not messagebox.askyesno(
                    "Backup Failed",
                    "The backup failed.\n\n"
                    "Continue WITHOUT a backup?"
                ):

                    return


        # ----------------------------------------------------
        # Process
        # ----------------------------------------------------

        self.log(
            "\n========================================\n"
            "Starting subsystem processing\n"
            f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n"
            f"Kernel: {kernel_dir}\n"
            "========================================\n\n"
        )


        for name in selected:

            self.log(
                f"\n--- Processing {name} ---\n"
            )

            spec = SUBSYSTEMS[name]


            # ----------------------------------------------
            # Delete directories
            # ----------------------------------------------

            for rel_dir in spec["dirs"]:

                target = (
                    kernel_dir /
                    rel_dir
                )

                self.remove_directory(
                    target,
                    dry_run
                )


            # ----------------------------------------------
            # Modify build references
            # ----------------------------------------------

            for (
                rel_file,
                pattern,
                replacement
            ) in spec["files"]:

                full_path = (
                    kernel_dir /
                    rel_file
                )

                self.comment_out_line(
                    full_path,
                    pattern,
                    replacement,
                    dry_run
                )


            self.log(
                f"--- Finished {name} ---\n"
            )


        self.log(
            "\n========================================\n"
            "Subsystem processing completed.\n"
            "========================================\n"
        )


        if dry_run:

            self.log(
                "\nDRY RUN ONLY — no changes were made.\n"
                "Disable Dry Run when you are satisfied.\n\n"
            )

            messagebox.showinfo(
                "Dry Run Complete",
                "Dry run completed.\n\n"
                "No files were changed."
            )

        else:

            self.log(
                "\nIMPORTANT:\n"
                "Run Build Kernel to validate the modified tree.\n\n"
            )

            messagebox.showinfo(
                "Removal Complete",
                "Selected subsystem removal completed.\n\n"
                "Run 'Build Kernel' to validate the result."
            )


    # ========================================================
    # BUILD KERNEL
    # ========================================================

    def build_kernel(self):

        if self.build_running:

            messagebox.showwarning(
                "Build Running",
                "A kernel build is already running."
            )

            return


        kernel_dir = Path(
            self.kernel_dir_var.get()
        ).expanduser()


        valid, error = self.validate_kernel_directory(
            kernel_dir
        )

        if not valid:

            messagebox.showerror(
                "Invalid Kernel Directory",
                error
            )

            return


        self.save_config()


        # ----------------------------------------------------
        # Confirm build
        # ----------------------------------------------------

        if not messagebox.askyesno(
            "Build Kernel",
            "Build the kernel using:\n\n"
            "1. olddefconfig\n"
            "2. clean\n"
            "3. zImage + DTBs\n\n"
            "Continue?"
        ):

            return


        self.build_running = True

        self.apply_btn.config(
            state=tk.DISABLED
        )

        self.build_btn.config(
            state=tk.DISABLED
        )


        self.log(
            "\n========================================\n"
            " Starting Linux Kernel Build\n"
            "========================================\n\n"
        )


        commands = [

            [
                "make",
                "ARCH=arm",
                "CROSS_COMPILE=arm-linux-gnueabihf-",
                "HOSTCC=gcc",
                "HOSTLD=gcc",
                "olddefconfig",
            ],

            [
                "make",
                "ARCH=arm",
                "CROSS_COMPILE=arm-linux-gnueabihf-",
                "HOSTCC=gcc",
                "HOSTLD=gcc",
                "clean",
            ],

            [
                "make",
                "ARCH=arm",
                "CROSS_COMPILE=arm-linux-gnueabihf-",
                "HOSTCC=gcc",
                "HOSTLD=gcc",
                "-j4",
                "zImage",
                "dtbs",
            ],
        ]


        def run_build():

            success = True


            for command in commands:

                self.log(
                    "\n$ "
                    + " ".join(command)
                    + "\n\n"
                )


                try:

                    process = subprocess.Popen(
                        command,
                        cwd=kernel_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )


                    for line in iter(
                        process.stdout.readline,
                        ""
                    ):

                        if line:

                            self.log(line)


                    process.stdout.close()

                    return_code = (
                        process.wait()
                    )


                    if return_code != 0:

                        success = False

                        self.log(
                            "\n"
                            "ERROR: Command failed.\n"
                            f"Return code: {return_code}\n"
                        )

                        break


                    self.log(
                        "\n"
                        "Command completed successfully.\n"
                    )


                except Exception as e:

                    success = False

                    self.log(
                        "\n"
                        f"EXCEPTION: {e}\n"
                    )

                    break


            self.build_finished(
                success
            )


        threading.Thread(
            target=run_build,
            daemon=True
        ).start()


    # ========================================================
    # BUILD FINISHED
    # ========================================================

    def build_finished(self, success):

        def finish():

            self.build_running = False

            self.apply_btn.config(
                state=tk.NORMAL
            )

            self.build_btn.config(
                state=tk.NORMAL
            )


            if success:

                self.log(
                    "\n========================================\n"
                    " BUILD COMPLETED SUCCESSFULLY\n"
                    "========================================\n\n"
                )

                messagebox.showinfo(
                    "Build Successful",
                    "Kernel build completed successfully."
                )

            else:

                self.log(
                    "\n========================================\n"
                    " BUILD FAILED\n"
                    "========================================\n\n"
                )

                messagebox.showerror(
                    "Build Failed",
                    "The kernel build failed.\n\n"
                    "Check the log for the first error."
                )


        self.root.after(
            0,
            finish
        )


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    app = KernelNannyGUI(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()