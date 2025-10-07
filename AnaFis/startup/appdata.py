"""App data directory utilities for AnaFis startup."""

import logging
import os


def ensure_app_data_directories() -> None:
    """Ensure the application data directory exists."""
    try:
        if os.name == "nt":
            appdata_local = os.environ.get("LOCALAPPDATA")
            if appdata_local:
                app_data_dir = os.path.join(appdata_local, "AnaFis")
            else:
                app_data_dir = os.path.expanduser("~\\AppData\\Local\\AnaFis")
        else:
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                app_data_dir = os.path.join(xdg_config, "anafis")
            else:
                app_data_dir = os.path.expanduser("~/.config/anafis")
        os.makedirs(app_data_dir, exist_ok=True)
        logging.info("Application data directory verified/created")
    except OSError as e:
        logging.warning("Could not create application data directories: %s", e)
