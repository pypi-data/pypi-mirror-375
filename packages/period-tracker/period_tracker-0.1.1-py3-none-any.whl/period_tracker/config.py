import json
import os
from pathlib import Path
import sys

APP_NAME = "period-tracker"


def get_config_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.getenv("APPDATA")) / APP_NAME
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME


def get_config_path() -> Path:
    return get_config_dir() / "config.json"


def load_config() -> dict:
    path = get_config_path()
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def get_gpg_recipient() -> str:
    try:
        config = load_config()
        return config["gpg_recipient"]
    except (FileNotFoundError, KeyError):
        import tkinter.simpledialog as sd
        import tkinter.messagebox as mb
        from tkinter import Tk

        root = Tk()
        root.withdraw()  # hide main window
        recipient = sd.askstring(
            "GPG Key Setup", "Enter your GPG key email, ID or fingerprint:"
        )
        if not recipient:
            mb.showerror("Missing Key", "No GPG key provided.")
            raise SystemExit(1)
        save_config({"gpg_recipient": recipient})
        return recipient


def load_luteal_phase() -> int:
    """Load the custom luteal phase length from the config."""
    config = load_config()
    return config.get("luteal_phase_len", 14)  # Default to 14 if not set


def save_luteal_phase(luteal_phase_len: int) -> None:
    """Save the custom luteal phase length to the config."""
    config = load_config()
    config["luteal_phase_len"] = luteal_phase_len
    save_config(config)
