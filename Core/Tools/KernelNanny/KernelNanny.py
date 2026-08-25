#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

CONFIG_PATH = Path.home() / ".kernel_subsystem_remover_config.json"

DEFAULT_KERNEL_DIR = "../../linux"

SUBSYSTEMS = {
    "net": {
        "dirs": ["net", "drivers/net", "arch/arm/net"],
        "files": [
            # (relative file, line pattern to match, replacement line without comment)
            ("Kconfig", r'^source "net/Kconfig"', '# source "net/Kconfig"'),
            ("lib/Kconfig.debug", r'^source "net/Kconfig.debug"', '# source "net/Kconfig.debug"'),
            ("fs/Kconfig", r'^source "net/sunrpc/Kconfig"', '# source "net/sunrpc/Kconfig"'),
            ("Kbuild", r'^obj-\$\(CONFIG_NET\)\s*\+=\s*net/', '# obj-$(CONFIG_NET) += net/'),
            ("drivers/Makefile", r'^obj-y\s*\+=\s*net/', '# obj-y += net/'),
            ("drivers/Kconfig", r'^source "drivers/net/Kconfig"', '# source "drivers/net/Kconfig"'),
            ("arch/arm/Kbuild", r'^obj-y\s*\+=\s*net/', '# obj-y += net/'),
        ],
    },
    "sound": {
        "dirs": ["sound"],
        "files": [
            ("Kbuild", r'^obj-y\s*\+=\s*sound/', '# obj-y += sound/'),
            ("drivers/Kconfig", r'^source "sound/Kconfig"', '# source "sound/Kconfig"'),
        ],
    },
    "bluetooth": {
        "dirs": ["drivers/bluetooth", "include/net/bluetooth"],
        "files": [
            ("drivers/Kconfig", r'^source "drivers/bluetooth/Kconfig"', '# source "drivers/bluetooth/Kconfig"'),
            # Adjust the pattern to your actual line in drivers/Makefile
            ("drivers/Makefile", r'^obj-\$\(CONFIG_BT\)\s*\+=\s*bluetooth/', '# obj-$(CONFIG_BT) += bluetooth/'),
        ],
    },
    "virt": {
        "dirs": ["virt"],
        "files": [
            ("Kbuild", r'^obj-y\s*\+=\s*virt/', '# obj-y += virt/'),
            ("drivers/vfio/Kconfig", r'^source "virt/lib/Kconfig"', '# source "virt/lib/Kconfig"'),
            ("drivers/Makefile", r'^obj-\$\(CONFIG_VIRT_DRIVERS\)\s*\+=\s*virt/', '# obj-$(CONFIG_VIRT_DRIVERS) += virt/'),
        ],
    },
}


class KernelNannyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CubeSat2030 KernelNanny")
        self.root.geometry("800x600")

        # Load config
        self.config = self.load_config()

        # Kernel directory
        tk.Label(root, text="Kernel Source Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.kernel_dir_var = tk.StringVar(value=self.config.get("kernel_dir", DEFAULT_KERNEL_DIR))
        tk.Entry(root, textvariable=self.kernel_dir_var, width=80).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.browse_kernel_dir).grid(row=0, column=2, padx=5, pady=5)

        # Subsystem checkboxes
        tk.Label(root, text="Select subsystems to remove:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.subsystem_vars = {}
        row = 2
        for name in SUBSYSTEMS:
            var = tk.BooleanVar(value=(name in self.config.get("selected_subsystems", [])))
            self.subsystem_vars[name] = var
            tk.Checkbutton(root, text=name, variable=var).grid(row=row, column=0, sticky="w", padx=20)
            row += 1

        # Buttons
        self.apply_btn = tk.Button(root, text="Apply Removals", command=self.apply_removals, bg="#f0a0a0")
        self.apply_btn.grid(row=row, column=0, padx=5, pady=10, sticky="w")

        self.build_btn = tk.Button(root, text="Build Kernel (olddefconfig + clean + zImage dtbs)", command=self.build_kernel)
        self.build_btn.grid(row=row, column=1, padx=5, pady=10, sticky="w")

        # Log area
        self.log_text = scrolledtext.ScrolledText(root, width=90, height=25, state='normal')
        self.log_text.grid(row=row+1, column=0, columnspan=3, padx=5, pady=5)

        self.log("Welcome. Configure settings and press 'Apply Removals' or 'Build Kernel'.\n")

    def load_config(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        config = {
            "kernel_dir": self.kernel_dir_var.get(),
            "selected_subsystems": [name for name, var in self.subsystem_vars.items() if var.get()],
        }
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.log(f"Warning: could not save config: {e}\n")

    def browse_kernel_dir(self):
        directory = filedialog.askdirectory(initialdir=self.kernel_dir_var.get())
        if directory:
            self.kernel_dir_var.set(directory)

    def log(self, message):
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def comment_out_line(self, file_path, pattern, replacement):
        """Read file, comment out lines matching pattern by prepending '#' if not already commented."""
        path = Path(file_path)
        if not path.exists():
            self.log(f"  File not found: {path}\n")
            return
        lines = path.read_text().splitlines()
        changed = False
        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()) and not line.lstrip().startswith('#'):
                lines[i] = replacement
                changed = True
        if changed:
            path.write_text('\n'.join(lines) + '\n')
            self.log(f"  Commented out in {path.name}:\n    {replacement}\n")
        else:
            self.log(f"  No active match in {path.name} for pattern:\n    {pattern}\n")

    def apply_removals(self):
        kernel_dir = Path(self.kernel_dir_var.get())
        if not kernel_dir.exists() or not kernel_dir.is_dir():
            messagebox.showerror("Error", "Kernel directory does not exist.")
            return

        selected = [name for name, var in self.subsystem_vars.items() if var.get()]
        if not selected:
            messagebox.showinfo("Nothing selected", "Please select at least one subsystem to remove.")
            return

        self.save_config()

        for name in selected:
            self.log(f"Processing subsystem: {name}\n")
            spec = SUBSYSTEMS[name]

            # Delete directories
            for rel_dir in spec["dirs"]:
                target = kernel_dir / rel_dir
                if target.exists():
                    try:
                        if target.is_dir():
                            shutil.rmtree(target)
                            self.log(f"  Deleted directory: {target}\n")
                        else:
                            target.unlink()
                            self.log(f"  Deleted file: {target}\n")
                    except Exception as e:
                        self.log(f"  Error deleting {target}: {e}\n")
                else:
                    self.log(f"  Directory already absent: {target}\n")

            # Comment out references
            for rel_file, pattern, replacement in spec["files"]:
                full_path = kernel_dir / rel_file
                self.comment_out_line(full_path, pattern, replacement)

            self.log(f"Finished {name}.\n\n")

        self.log("All selected removals completed.\n")

    def build_kernel(self):
        kernel_dir = Path(self.kernel_dir_var.get())
        if not kernel_dir.exists() or not kernel_dir.is_dir():
            messagebox.showerror("Error", "Kernel directory does not exist.")
            return

        self.save_config()
        self.log("Starting kernel build...\n")

        commands = [
            ["make", "ARCH=arm", "CROSS_COMPILE=arm-linux-gnueabihf-", "HOSTCC=gcc", "HOSTLD=gcc", "olddefconfig"],
            ["make", "ARCH=arm", "CROSS_COMPILE=arm-linux-gnueabihf-", "HOSTCC=gcc", "HOSTLD=gcc", "clean"],
            ["make", "ARCH=arm", "CROSS_COMPILE=arm-linux-gnueabihf-", "HOSTCC=gcc", "HOSTLD=gcc", "-j4", "zImage", "dtbs"],
        ]

        def run_build():
            for cmd in commands:
                self.log(f"Running: {' '.join(cmd)}\n")
                try:
                    result = subprocess.run(cmd, cwd=kernel_dir, capture_output=True, text=True)
                    if result.stdout:
                        self.log(result.stdout[-1000:])  # show last 1000 chars to avoid flooding
                    if result.returncode != 0:
                        self.log(f"ERROR: command failed with return code {result.returncode}\n")
                        if result.stderr:
                            self.log(result.stderr[-2000:])
                        break
                except Exception as e:
                    self.log(f"Exception: {e}\n")
                    break
            else:
                self.log("Build completed successfully.\n")

        threading.Thread(target=run_build, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = KernelNannyGUI(root)
    root.mainloop()