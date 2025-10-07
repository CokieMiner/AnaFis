"""
Enhanced theme manager for AnaFis application.
Manages application themes including built-in TTK themes and custom TCL themes
with improved performance monitoring and caching.
"""

import logging
import os
import tkinter as tk
from tkinter import ttk
from typing import List, Set, Any, Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum
import time


class ThemeType(Enum):
    """Types of themes supported"""

    TTK_BUILTIN = "ttk_builtin"
    TTK_PACKAGE = "ttk_package"


@dataclass
class ThemeInfo:
    """Information about a theme"""

    name: str
    type: ThemeType
    display_name: str
    description: Optional[str] = None
    load_time: Optional[float] = None
    error: Optional[str] = None


class ThemeManager:
    """Singleton class to manage application themes, including built-in, package, and custom themes.
    Provides theme loading, application, caching, and adaptive color support for AnaFis.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args: Any, **kwargs: Any):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        logging.info("Creating ThemeManager singleton instance.")
        self.available_themes: List[ThemeInfo] = []
        self.root: Optional[tk.Tk] = None
        self._initialized = False
        self._color_callbacks: List[Callable[[], None]] = []

        # Performance optimizations
        self._theme_colors_cache: Dict[str, Dict[str, str]] = {}

        # Theme loading statistics
        self._load_times: Dict[str, float] = {}
        self._load_errors: Dict[str, str] = {}

        # Current theme tracking
        self._current_theme: Optional[str] = None
        self._theme_history: List[str] = []

    @property
    def is_initialized(self) -> bool:
        """Returns True if the theme manager has been initialized."""
        return self._initialized

    def initialize(self, root: tk.Tk):
        """Initializes the theme manager with the application's root window."""
        if self._initialized:
            logging.warning("ThemeManager is already initialized.")
            return

        logging.info("Initializing ThemeManager with application root...")
        self.root = root
        self._load_all_themes()
        self._initialized = True
        logging.info(
            f"ThemeManager initialized. {len(self.available_themes)} themes available."
        )

        # Start background theme optimization
        self._optimize_theme_performance()

    def _optimize_theme_performance(self) -> None:
        """Optimize theme performance by preloading common themes"""
        try:
            # Preload common themes in background
            common_themes = ["vista", "clam", "alt"]
            for theme_name in common_themes:
                if theme_name in [t.name for t in self.available_themes]:
                    self._preload_theme_colors(theme_name)
        except Exception as e:
            logging.debug(f"Theme optimization failed: {e}")

    def _preload_theme_colors(self, theme_name: str) -> None:
        """Preload theme colors for faster access"""
        if theme_name in self._theme_colors_cache:
            return

        try:
            start_time = time.time()

            # Create a temporary style to extract colors
            temp_style = ttk.Style()
            temp_style.theme_use(theme_name)

            # Extract common colors
            colors = {
                "background": self._get_style_color(temp_style, "TFrame", "background"),
                "foreground": self._get_style_color(temp_style, "TLabel", "foreground"),
                "text_info": self._get_style_color(temp_style, "TLabel", "foreground"),
                "text_error": "#ff0000",  # Default error color
                "text_success": "#008000",  # Default success color
                "text_warning": "#ffa500",  # Default warning color
                "text_valid": "#008000",  # Default valid color
            }

            self._theme_colors_cache[theme_name] = colors
            self._load_times[theme_name] = time.time() - start_time

        except Exception as e:
            logging.debug(f"Failed to preload colors for {theme_name}: {e}")
            self._load_errors[theme_name] = str(e)

    def _get_style_color(self, style: ttk.Style, element: str, option: str) -> str:
        """Safely get a color from a style"""
        try:
            return style.lookup(element, option) or "#000000"
        except (tk.TclError, Exception):
            return "#000000"

    def get_themes_directory(self) -> str:
        """Get the themes directory path"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "..", "..", "themes")

    def _load_all_themes(self) -> None:
        """Load all available themes (built-in TTK and package themes)"""
        self.available_themes.clear()

        # Load built-in TTK themes
        self._load_builtin_ttk_themes()

        # Load package themes (ttkthemes)
        self._load_package_themes()

        logging.info(f"Loaded {len(self.available_themes)} themes total")

    def _load_builtin_ttk_themes(self) -> None:
        """Load built-in TTK themes"""
        if not self.root:
            return

        try:
            style = ttk.Style(self.root)
            builtin_themes = style.theme_names()

            for theme_name in builtin_themes:
                theme_info = ThemeInfo(
                    name=theme_name,
                    type=ThemeType.TTK_BUILTIN,
                    display_name=theme_name.title(),
                    description=f"Built-in TTK theme: {theme_name}",
                )
                self.available_themes.append(theme_info)

        except Exception as e:
            logging.error(f"Error loading built-in TTK themes: {e}")

    def _load_package_themes(self) -> None:
        """Load themes from ttkthemes package"""
        try:
            import ttkthemes
            # Get available themed styles
            themed_style = ttkthemes.ThemedStyle(self.root)
            package_themes = themed_style.theme_names()

            for theme_name in package_themes:
                # Skip if already loaded as built-in
                if any(t.name == theme_name for t in self.available_themes):
                    continue

                theme_info = ThemeInfo(
                    name=theme_name,
                    type=ThemeType.TTK_PACKAGE,
                    display_name=theme_name.title(),
                    description=f"ttkthemes package theme: {theme_name}",
                )
                self.available_themes.append(theme_info)

            logging.info(f"Loaded {len(package_themes)} ttkthemes package themes")
        except ImportError:
            logging.info("ttkthemes package not available, skipping package themes")
        except Exception as e:
            logging.error(f"Error loading package themes: {e}")

    def apply_theme(self, theme_name: str) -> bool:
        """Apply a theme with enhanced error handling and performance tracking"""
        if not self.root:
            logging.error("ThemeManager not initialized")
            return False

        try:
            start_time = time.time()

            # Find theme info
            theme_info = self._find_theme_info(theme_name)
            if not theme_info:
                logging.error("Theme '%s' not found", theme_name)
                return False

            # Apply the theme based on its type
            if theme_info.type == ThemeType.TTK_PACKAGE:
                success = self._apply_package_theme(theme_name)
            else:
                success = self._apply_ttk_theme(theme_name)

            if success:
                self._current_theme = theme_name
                self._theme_history.append(theme_name)
                if len(self._theme_history) > 10:  # Keep last 10 themes
                    self._theme_history.pop(0)

                # Preload colors for the new theme
                self._preload_theme_colors(theme_name)

                # Notify callbacks
                self._notify_color_callbacks()

                load_time = time.time() - start_time
                logging.info(
                    "Theme '%s' applied successfully in %.3fs", theme_name, load_time
                )
                return True
            else:
                logging.error("Failed to apply theme '%s'", theme_name)
                return False

        except Exception as e:
            logging.error("Error applying theme '%s': %s", theme_name, e)
            return False

    def _find_theme_info(self, theme_name: str) -> Optional[ThemeInfo]:
        """Find theme info by name"""
        for theme in self.available_themes:
            if theme.name == theme_name:
                return theme
        return None

    def _apply_ttk_theme(self, theme_name: str) -> bool:
        """Apply a TTK theme"""
        try:
            style = ttk.Style(self.root)
            style.theme_use(theme_name)
            return True
        except Exception as e:
            logging.error("Error applying TTK theme '%s': %s", theme_name, e)
            return False

    def _apply_package_theme(self, theme_name: str) -> bool:
        """Apply a ttkthemes package theme"""
        try:
            import ttkthemes
            themed_style = ttkthemes.ThemedStyle(self.root)
            themed_style.set_theme(theme_name)
            return True
        except ImportError:
            logging.error("ttkthemes package not available for theme '%s'", theme_name)
            return False
        except Exception as e:
            logging.error("Error applying package theme '%s': %s", theme_name, e)
            return False

    def get_adaptive_color(self, color_type: str) -> str:
        """Get an adaptive color based on the current theme"""
        if not self._current_theme:
            return self._get_default_color(color_type)

        # Check cache first
        if self._current_theme in self._theme_colors_cache:
            cached_colors = self._theme_colors_cache[self._current_theme]
            if color_type in cached_colors:
                return cached_colors[color_type]

        # Fallback to default colors
        return self._get_default_color(color_type)

    def _get_default_color(self, color_type: str) -> str:
        """Get default colors"""
        default_colors = {
            "background": "#f0f0f0",
            "foreground": "#000000",
            "text_info": "#666666",
            "text_error": "#ff0000",
            "text_success": "#008000",
            "text_warning": "#ffa500",
            "text_valid": "#008000",
        }
        return default_colors.get(color_type, "#000000")

    def get_available_themes(self) -> List[ThemeInfo]:
        """Get list of available themes"""
        return self.available_themes.copy()

    def get_current_theme(self) -> Optional[str]:
        """Get the currently applied theme"""
        return self._current_theme

    def register_color_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when colors change"""
        self._color_callbacks.append(callback)

    def unregister_color_callback(self, callback: Callable[[], None]) -> None:
        """Unregister a previously registered color callback"""
        try:
            self._color_callbacks.remove(callback)
        except ValueError:
            # Callback wasn't registered, ignore
            pass

    def _notify_color_callbacks(self) -> None:
        """Notify all registered callbacks"""
        for callback in self._color_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error("Error in color callback: %s", e)

    def clear_cache(self) -> None:
        """Clear theme color cache"""
        self._theme_colors_cache.clear()
        self._load_times.clear()
        self._load_errors.clear()


# Global theme manager instance
theme_manager = ThemeManager()
