import tkinter as tk
from period_tracker.gui.layout import PeriodTrackerUI
from period_tracker.config import get_gpg_recipient

import shutil
import sys


def check_gpg_installed():
    if shutil.which("gpg") is None:
        print(
            "Error: GPG is not installed or not in your system PATH.\n"
            "Please install GnuPG from https://gnupg.org/download/ and ensure 'gpg.exe' is in your PATH.",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    _ = get_gpg_recipient()
    root = tk.Tk()
    root.geometry("1280x460")
    PeriodTrackerUI(root)
    root.mainloop()


if __name__ == "__main__":
    check_gpg_installed()
    main()
