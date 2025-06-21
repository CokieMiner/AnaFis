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
from .constants import TRANSLATIONS


class UserPreferencesManager:
    """Manages user preferences for the application."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the preferences manager.        Args:
            config_dir: Custom configuration directory. If None, uses default user config directory.
        """
        if config_dir is None:
            # Windows
            if os.name == 'nt':
                appdata_local = os.environ.get('LOCALAPPDATA')
                if appdata_local:
                    config_dir = os.path.join(appdata_local, 'AnaFis')
                else:
                    # Fallback if LOCALAPPDATA is not available
                    config_dir = os.path.expanduser('~\\AppData\\Local\\AnaFis')
            else:
                # For Unix-like systems, use XDG config directory or fallback to ~/.config
                xdg_config = os.environ.get('XDG_CONFIG_HOME')
                if xdg_config:
                    config_dir = os.path.join(xdg_config, 'anafis')
                else:
                    config_dir = os.path.expanduser('~/.config/anafis')

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'user_preferences.json'

        # Default preferences - properly typed
        self.default_preferences: Dict[str, Any] = {
            'language': 'pt',
            'theme': 'vista',
            'font_size': 12,
            'decimal_places': 4,
            'graph_dpi': 100,
            'export_format': 'png',
            'remember_window_size': True,
            'show_tooltips': True,
            'advanced_mode': False,
            'last_export_directory': '',
            'recent_files': [],
            'max_recent_files': 10,
            'confirm_exit': True,
            'show_welcome_screen': True,
            'check_updates': True,
            'auto_check_updates': True
        }

        self.available_languages: List[str] = list(TRANSLATIONS.keys())

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

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except ValueError as e:  # Catch validation errors
            # Optionally, re-raise or handle more gracefully depending on desired app behavior
            # For now, we log and return False, consistent with IO/JSON errors
            logging.error(f"Validation error for preference '{key}': {e}")
            return False
        except (IOError, JSONDecodeError) as e:
            logging.error(f"Error saving preference '{key}': {e}")
            return False

    def get_all_preferences(self) -> Dict[str, Any]:
        """
        Get all preferences.

        Returns:
            Dictionary of all preferences
        """
        config = self._load_config()
        # Merge with defaults for any missing keys
        merged_config = self.default_preferences.copy()
        merged_config.update(config)
        return merged_config

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

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, JSONDecodeError) as e:
            logging.error(f"Error saving preferences: {e}")
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
        if key == 'language' and value not in self.available_languages:
            raise ValueError(
                f"Language '{value}' not available. Available languages: {self.available_languages}"
            )
        if key == 'theme':
            # Import theme manager to get available themes
            try:
                from .theme_manager import theme_manager
                available_themes = ["system"] + theme_manager.get_available_themes()
                if value not in available_themes:
                    raise ValueError(
                        f"Theme '{value}' not available. Available themes: {sorted(available_themes)}"
                    )
            except ImportError:
                # Fallback to basic validation if theme manager not available
                if value not in ['light', 'dark', 'auto', 'system', 'vista', 'xpnative', 'clam', 'default', 'alt', 'classic']:
                    raise ValueError(
                        f"Theme '{value}' not available. Available themes: ['system', 'vista', 'xpnative', 'clam', 'default', 'alt', 'classic']"
                    )
        if key == 'export_format' and value not in ['png', 'jpg', 'svg', 'pdf']:
            raise ValueError(
                f"Export format '{value}' not available. "
                f"Available formats: ['png', 'jpg', 'svg', 'pdf']"
            )
        if key == 'font_size' and (not isinstance(value, int) or value < 8 or value > 72):
            raise ValueError("Font size must be an integer between 8 and 72")
        if key == 'decimal_places' and (not isinstance(value, int) or value < 0 or value > 15):
            raise ValueError("Decimal places must be an integer between 0 and 15")
        if key == 'graph_dpi' and (not isinstance(value, int) or value < 50 or value > 300):
            raise ValueError("Graph DPI must be an integer between 50 and 300")
        if key == 'max_recent_files' and (not isinstance(value, int) or value < 0 or value > 50):
            raise ValueError("Max recent files must be an integer between 0 and 50")

    # Language-specific methods for backward compatibility and convenience
    def get_language(self) -> str:
        """
        Get the current language preference.

        Returns:
            Language code (e.g., 'pt', 'en')
        """
        return self.get_preference('language')

    def set_language(self, language: str) -> bool:
        """
        Set the language preference.

        Args:
            language: Language code to set

        Returns:
            True if successfully saved, False otherwise
        """
        return self.set_preference('language', language)

    def get_available_languages(self) -> List[str]:
        """
        Get list of available language codes.

        Returns:
            List of available language codes
        """
        return self.available_languages.copy()

    def get_language_name(self, language_code: str) -> str:
        """
        Get the display name for a language code.

        Args:
            language_code: The language code

        Returns:
            Human-readable language name
        """
        # Use the current language for display (from preferences)
        current_lang = self.get_preference('language', 'pt')
        
        # Use the translation system if available
        if language_code in ['pt', 'en'] and f'language_{language_code}' in TRANSLATIONS[current_lang]:
            return TRANSLATIONS[current_lang][f'language_{language_code}']
        
        # Fallback to a basic mapping
        language_names = {
            'pt': 'Português',
            'en': 'English'
        }
        return language_names.get(language_code, language_code)

    def get_translation(self, key: str, language: Optional[str] = None) -> str:
        """
        Get a translation for the given key.

        Args:
            key: Translation key
            language: Language code. If None, uses current language preference.

        Returns:
            Translated text or the key if translation not found
        """
        if language is None:
            language = self.get_language()

        try:
            return TRANSLATIONS[language][key]
        except KeyError:
            # Fall back to default language if key not found
            try:
                return TRANSLATIONS[self.default_preferences['language']][key]
            except KeyError:
                # If key not found in default language either, return the key itself
                return key

    # Recent files management
    def add_recent_file(self, file_path: str) -> bool:
        """
        Add a file to the recent files list.

        Args:
            file_path: Path of the file to add

        Returns:
            True if successfully saved, False otherwise
        """
        recent_files = self.get_preference('recent_files', [])
        max_recent = self.get_preference('max_recent_files', 10)

        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to beginning
        recent_files.insert(0, file_path)

        # Trim to max length
        recent_files = recent_files[:max_recent]

        return self.set_preference('recent_files', recent_files)

    def get_recent_files(self) -> List[str]:
        """
        Get the list of recent files.

        Returns:
            List of recent file paths
        """
        return self.get_preference('recent_files', [])

    def clear_recent_files(self) -> bool:
        """
        Clear the recent files list.

        Returns:
            True if successfully saved, False otherwise
        """
        return self.set_preference('recent_files', [])

    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration file.

        Returns:
            Configuration dictionary
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
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

    def reset_preference(self, key: str) -> bool:
        """
        Reset a specific preference to its default value.

        Args:
            key: The preference key to reset

        Returns:
            True if successfully reset, False otherwise
        """
        if key not in self.default_preferences:
            raise ValueError(f"Unknown preference key: {key}")

        return self.set_preference(key, self.default_preferences[key])

    def export_config(self, file_path: str) -> bool:
        """
        Export current configuration to a file.

        Args:
            file_path: Path to export configuration to

        Returns:
            True if successfully exported, False otherwise
        """
        try:
            config = self.get_all_preferences()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, JSONDecodeError) as e:
            logging.error(f"Error exporting configuration: {e}")
            return False

    def import_config(self, file_path: str, validate: bool = True) -> bool:
        """
        Import configuration from a file.

        Args:
            file_path: Path to import configuration from
            validate: Whether to validate imported preferences

        Returns:
            True if successfully imported, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if validate:
                # Validate critical preferences
                for key, value in config.items():
                    if key in self.default_preferences:
                        try:
                            self._validate_preference(key, value)
                        except ValueError as e:
                            logging.error(f"Invalid value for {key} in imported config: {e}")
                            return False

            # Import only known preferences to avoid pollution
            valid_config: Dict[str, Any] = {}
            for key, value in config.items():
                if key in self.default_preferences or not validate:
                    valid_config[key] = value

            return self.set_multiple_preferences(valid_config)
        except (IOError, JSONDecodeError, KeyError) as e:
            logging.error(f"Error importing configuration: {e}")
            return False

    def get_preference_info(self, key: str) -> Dict[str, Any]:
        """
        Get information about a specific preference.

        Args:
            key: The preference key

        Returns:
            Dictionary with preference information
        """
        info: Dict[str, Any] = {
            'key': key,
            'current_value': self.get_preference(key),
            'default_value': self.default_preferences.get(key),
            'exists': key in self.default_preferences
        }

        # Add type information
        if key in self.default_preferences:
            info['type'] = type(self.default_preferences[key]).__name__

        # Add validation info for specific preferences
        if key == 'language':
            info['valid_values'] = self.available_languages
        elif key == 'theme':
            info['valid_values'] = ['light', 'dark', 'auto']
        elif key == 'export_format':
            info['valid_values'] = ['png', 'jpg', 'svg', 'pdf']
        elif key == 'font_size':
            info['range'] = [8, 72]
        elif key == 'decimal_places':
            info['range'] = [0, 15]
        elif key == 'graph_dpi':
            info['range'] = [50, 300]
        elif key == 'max_recent_files':
            info['range'] = [0, 50]

        return info

    def get_all_preference_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all preferences.

        Returns:
            Dictionary with information about all preferences
        """
        return {key: self.get_preference_info(key) for key in self.default_preferences}


# Global instance for easy access
user_preferences = UserPreferencesManager()


# Convenience functions for common preferences
def get_current_language() -> str:
    """Convenience function to get current language."""
    return user_preferences.get_language()


def set_current_language(language: str) -> bool:
    """Convenience function to set current language."""
    return user_preferences.set_language(language)


def translate(key: str, language: Optional[str] = None) -> str:
    """Convenience function to get translations."""
    return user_preferences.get_translation(key, language)


def get_preference(key: str, default: Any = None) -> Any:
    """Convenience function to get a preference."""
    return user_preferences.get_preference(key, default)


def set_preference(key: str, value: Any) -> bool:
    """Convenience function to set a preference."""
    return user_preferences.set_preference(key, value)


def get_theme() -> str:
    """Convenience function to get current theme."""
    return user_preferences.get_preference('theme', 'vista')


def set_theme(theme: str) -> bool:
    """Convenience function to set theme."""
    return user_preferences.set_preference('theme', theme)


def get_font_size() -> int:
    """Convenience function to get font size."""
    return user_preferences.get_preference('font_size', 12)


def set_font_size(size: int) -> bool:
    """Convenience function to set font size."""
    return user_preferences.set_preference('font_size', size)
