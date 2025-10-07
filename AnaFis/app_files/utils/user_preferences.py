"""
User preferences manager for the AnaFis application.
Handles saving and loading user preferences including language, UI settings, and more.
"""

import json
from json.decoder import JSONDecodeError
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, cast


class UserPreferencesManager:
    """Manages user preferences for the application."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the preferences manager.
        Args:
            config_dir: Custom configuration directory. If None, uses default user config directory.
        """
        if config_dir is None:
            # Windows
            if os.name == "nt":
                appdata_local = os.environ.get("LOCALAPPDATA")
                if appdata_local:
                    config_dir = os.path.join(appdata_local, "AnaFis")
                else:
                    # Fallback if LOCALAPPDATA is not available
                    config_dir = os.path.expanduser("~\\AppData\\Local\\AnaFis")
            else:
                # For Unix-like systems, use XDG config directory or fallback to ~/.config
                xdg_config = os.environ.get("XDG_CONFIG_HOME")
                if xdg_config:
                    config_dir = os.path.join(xdg_config, "anafis")
                else:
                    config_dir = os.path.expanduser("~/.config/anafis")

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "user_preferences.json"

        # Default preferences - properly typed
        self.default_preferences: Dict[str, Any] = {
            "language": "pt",
            "theme": "plastik",
            "font_size": 12,
            "decimal_places": 4,
            "graph_dpi": 100,
            "export_format": "png",
            "remember_window_size": True,
            "show_tooltips": True,
            "advanced_mode": False,
            "last_export_directory": "",
            "recent_files": [],
            "max_recent_files": 10,
            "confirm_exit": True,
            "show_welcome_screen": True,
            "check_updates": True,
            "auto_check_updates": True,
        }

        self.available_languages: List[str] = ["pt", "en"]

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a specific preference value.

        Args:
            key: The preference key
            default: Default value if key not found

        Returns:
            The preference value
        """
        config = self._load_config()
        if default is None:
            default = self.default_preferences.get(key)
        return config.get(key, default)

    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set a specific preference value.

        Args:
            key: The preference key
            value: The value to set

        Returns:
            True if successfully saved, False otherwise
        """
        try:
            # Validate first
            self._validate_preference(key, value)
            config = self._load_config()
            config[key] = value

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, ValueError, JSONDecodeError) as e:
            logging.error("Error saving preference '%s': %s", key, e)
            return False

    def set_multiple_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Set multiple preferences at once.

        Args:
            preferences: Dictionary of preference key-value pairs

        Returns:
            True if successfully saved, False otherwise
        """
        # Validate all preferences first
        for key, value in preferences.items():
            try:
                # Use a temporary validation by calling set_preference with dry run
                self._validate_preference(key, value)
            except ValueError as e:
                logging.error(f"Validation failed for {key}: {e}")
                return False

        try:
            config = self._load_config()
            config.update(preferences)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, JSONDecodeError) as e:
            logging.error("Error saving preferences: %s", e)
            return False

    def _validate_preference(self, key: str, value: Any) -> None:
        """
        Validate a preference value without saving it.

        Args:
            key: The preference key
            value: The value to validate

        Raises:
            ValueError: If the value is invalid
        """
        if key == "language" and value not in self.available_languages:
            raise ValueError(
                f"Language '{value}' not available. Available languages: {self.available_languages}"
            )

        # Get available themes from theme_manager
        if key == "theme":
            from app_files.utils.theme_manager import theme_manager

            if theme_manager.is_initialized:
                available_theme_names = [
                    t.name for t in theme_manager.get_available_themes()
                ]
                if value not in available_theme_names:
                    raise ValueError(
                        f"Theme '{value}' not available. Available themes: {available_theme_names}"
                    )

        if key == "export_format" and value not in ["png", "jpg", "svg", "pdf"]:
            raise ValueError(
                f"Export format '{value}' not available. "
                f"Available formats: ['png', 'jpg', 'svg', 'pdf']"
            )
        if key == "font_size" and (
            not isinstance(value, int) or value < 8 or value > 72
        ):
            raise ValueError("Font size must be an integer between 8 and 72")
        if key == "decimal_places" and (
            not isinstance(value, int) or value < 0 or value > 15
        ):
            raise ValueError("Decimal places must be an integer between 0 and 15")
        if key == "graph_dpi" and (
            not isinstance(value, int) or value < 50 or value > 300
        ):
            raise ValueError("Graph DPI must be an integer between 50 and 300")
        if key == "max_recent_files" and (
            not isinstance(value, int) or value < 0 or value > 50
        ):
            raise ValueError("Max recent files must be an integer between 0 and 50")

    # Language-specific methods for backward compatibility and convenience
    def get_language(self) -> str:
        """
        Get the current language preference.

        Returns:
            Language code (e.g., 'pt', 'en')
        """
        return self.get_preference("language")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration file.

        Returns:
            Configuration dictionary
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_json = json.load(f)
                if isinstance(loaded_json, dict):
                    return cast(Dict[str, Any], loaded_json)
                # Return empty dict if JSON root is not a dict (e.g. null, list)
                return {}
            else:
                return {}
        except (JSONDecodeError, IOError):
            # Error reading or parsing JSON, or file not found during open
            return {}

    def reset_to_defaults(self) -> bool:
        """
        Reset all preferences to default values.

        Returns:
            True if successfully reset, False otherwise
        """
        return self.set_multiple_preferences(self.default_preferences.copy())


# Global instance for easy access
user_preferences = UserPreferencesManager()
