# pylint: disable=broad-except
"""Main application module"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import logging
import os
import threading
import platform
from typing import Any, Dict, Optional, Callable, Literal

# Import the version from app_files package
from app_files import __version__

from app_files.utils.user_preferences import user_preferences
from app_files.utils.lazy_loader import lazy_import
from app_files.utils.translations.api import get_string, get_language_code_from_name
from app_files.utils.error_handler import show_error
from app_files.utils.tab_manager import TabManager


# Lazy imports for heavy GUI components - these will only load when needed
# High priority modules that are commonly used
AjusteCurvaFrame = lazy_import(
    "app_files.gui.ajuste_curva.main_gui",
    "AjusteCurvaFrame",
    preload_priority=5,
    dependencies=["numpy", "matplotlib"],
)
CalculoIncertezasFrame = lazy_import(
    "app_files.gui.incerteza.calculo_incertezas_gui",
    "CalculoIncertezasFrame",
    preload_priority=3,
    dependencies=["sympy"],
)
SettingsDialog = lazy_import(
    "app_files.gui.settings.settings_dialog", "SettingsDialog", preload_priority=1
)

# Type aliases for better type safety
LanguageType = Literal["pt", "en"]
TabType = Literal["curve_fitting", "uncertainty_calc", "home", "settings"]


class AplicativoUnificado:
    """Main application class with tabbed interface"""

    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        # Use provided root or create a new one
        if root is not None:
            self.root = root
        else:
            self.root = tk.Tk()

        self.language: LanguageType = user_preferences.get_preference("language", "pt")

        self.lang_label: Optional[ttk.Label] = None
        self.lang_var: Optional[tk.StringVar] = None
        self.lang_dropdown: Optional[ttk.Combobox] = None
        self.toolbar_frame: Optional[ttk.Frame] = None
        self.notebook: Optional[ttk.Notebook] = None
        self.home_tab: Optional[ttk.Frame] = None
        self.tab_menu: Optional[tk.Menu] = None
        self.icon: Optional[tk.PhotoImage] = None
        self.tab_manager: Optional[TabManager] = None
        if root is None:
            self.setup_ui()

    def setup_ui(self):
        """Set up the main UI components and window properties."""
        try:
            self.set_app_icon()
            self.root.title(get_string("main_app", "app_title", self.language))
            self.setup_toolbar()
            self.setup_notebook()
            self.tab_menu = tk.Menu(self.root, tearoff=0)
            self.tab_menu.add_command(label="Close", command=self.close_current_tab)
            self.root.geometry("1200x800")
            self.root.resizable(True, True)
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(1, weight=1)
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        except Exception as e:
            logging.error("Error during UI setup: %s", e)
            try:
                show_error(
                    get_string("main_app", "error", self.language),
                    get_string("main_app", "ui_setup_error", self.language),
                )
            except Exception:
                show_error("Error", str(e))

    def set_app_icon(self):
        """Set the application icon if available."""
        try:
            # Only set icon if not already set (Tkinter quirk: _icon_set is not a public attribute)
            if getattr(
                self.root, "_icon_set", False
            ):  # safer than hasattr+direct access
                return
            current_dir = os.path.dirname(os.path.abspath(__file__))
            utils_dir = os.path.join(current_dir, "utils")
            icon_path = os.path.join(utils_dir, "icon.png")
            if not os.path.exists(icon_path):
                logging.warning("Icon file not found at: %s", icon_path)
                return
            icon = tk.PhotoImage(file=icon_path, name=f"main_app_icon_{id(self)}")
            self.root.iconphoto(True, icon)
            self.icon = icon
            # _icon_set is not a public attribute,
            # but is used to avoid icon conflicts with splash screen
            setattr(
                self.root, "_icon_set", True
            )  # justified: avoids repeated icon setting
        except (OSError, tk.TclError) as e:
            logging.error("Error setting application icon: %s", e)
            try:
                show_error(
                    get_string("main_app", "error", self.language),
                    get_string("main_app", "icon_error", self.language),
                )
            except Exception:
                show_error("Error", str(e))

    def setup_toolbar(self):
        """Set up the toolbar with curve fitting, uncertainty, and language selector controls."""
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.toolbar_frame.columnconfigure(0, weight=0)
        self.toolbar_frame.columnconfigure(1, weight=0)
        self.toolbar_frame.columnconfigure(2, weight=1)
        self.toolbar_frame.columnconfigure(3, weight=0)
        curve_fit_btn = ttk.Button(
            self.toolbar_frame,
            text=get_string("main_app", "curve_fitting", self.language),
            command=self.open_curve_fitting_tab,
        )
        curve_fit_btn.grid(row=0, column=0, padx=5, sticky="w")
        uncertainty_btn = ttk.Button(
            self.toolbar_frame,
            text=get_string("main_app", "uncertainty_calc", self.language),
            command=self.open_uncertainty_calc_tab,
        )
        uncertainty_btn.grid(row=0, column=1, padx=5, sticky="w")
        self.setup_language_selector()

    def setup_language_selector(self) -> None:
        """Set up language selector in toolbar"""
        lang_frame = ttk.Frame(self.toolbar_frame)
        lang_frame.grid(row=0, column=3, padx=5, sticky="e")
        self.lang_label = ttk.Label(
            lang_frame, text=get_string("main_app", "language_label", self.language)
        )
        self.lang_label.grid(row=0, column=0, padx=(0, 5))
        self.lang_var = tk.StringVar(
            value=get_string("main_app", f"language_{self.language}", self.language)
        )
        self.lang_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=[
                get_string("main_app", "language_pt", self.language),
                get_string("main_app", "language_en", self.language),
            ],
            state="readonly",
            width=10,
        )
        self.lang_dropdown.grid(row=0, column=1)
        self.lang_dropdown.bind("<<ComboboxSelected>>", self.on_language_changed)

    def on_language_changed(self, event: Optional[Any] = None) -> None:
        # pylint: disable=unused-argument
        """Handle language change from dropdown"""
        if self.lang_var is None:
            return
        selected = self.lang_var.get()
        # Map the language display name back to language code
        new_language = get_language_code_from_name(selected, self.language)

        if new_language != self.language:
            self.language = new_language
            # Save the language preference
            user_preferences.set_preference("language", new_language)
            self.update_ui_language()

    def update_ui_language(self) -> None:
        """Update all UI elements to reflect the new language"""
        self.root.title(get_string("main_app", "app_title", self.language))
        self._update_toolbar_buttons()
        if self.lang_label is not None:
            self.lang_label.configure(
                text=get_string("main_app", "language_label", self.language)
            )
        if self.lang_dropdown is not None and self.lang_var is not None:
            current_lang_name: str = get_string(
                "main_app", f"language_{self.language}", self.language
            )
            self.lang_var.set(current_lang_name)
            self.lang_dropdown.configure(
                values=[
                    get_string("main_app", "language_pt", self.language),
                    get_string("main_app", "language_en", self.language),
                ]
            )
        if self.tab_manager:
            self.tab_manager.switch_language(self.language)

        # Update home tab content
        if self.home_tab:
            for widget in self.home_tab.winfo_children():
                widget.destroy()
            self.setup_home_tab()

    def setup_notebook(self):
        """Set up the main notebook widget and initialize the tab manager."""
        # This method is required for the UI setup; see Pylint E1101:no-member suppression.
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        # Add home tab on startup
        self.home_tab = ttk.Frame(self.notebook)
        self.notebook.add(
            self.home_tab, text=get_string("main_app", "home", self.language)
        )
        self.tab_manager = TabManager(self.notebook, self.home_tab, {}, self.language)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.setup_home_tab()

    def _update_toolbar_buttons(self) -> None:
        """Update toolbar button texts to current language."""
        if self.toolbar_frame is not None:
            for widget in self.toolbar_frame.winfo_children():
                if isinstance(widget, ttk.Button):
                    current_text = widget.cget("text")
                    # Check if it's the curve fitting button
                    if current_text in [
                        get_string("main_app", "curve_fitting", "pt"),
                        get_string("main_app", "curve_fitting", "en"),
                    ]:
                        widget.configure(
                            text=get_string("main_app", "curve_fitting", self.language)
                        )
                    # Check if it's the uncertainty calc button
                    elif current_text in [
                        get_string("main_app", "uncertainty_calc", "pt"),
                        get_string("main_app", "uncertainty_calc", "en"),
                    ]:
                        widget.configure(
                            text=get_string(
                                "main_app", "uncertainty_calc", self.language
                            )
                        )

    def close_current_tab(self) -> None:
        """Close the currently selected tab"""
        if self.notebook is None or not self.tab_manager:
            return
        try:
            selected_tab_path = self.notebook.select()
            if not selected_tab_path:
                return
            current_index = self.notebook.index(selected_tab_path)
            if isinstance(current_index, int):
                self.tab_manager.close_tab_at_index(current_index)
            else:
                logging.warning(
                    "Could not determine index for tab: %s",
                    str(selected_tab_path),
                )
        except (tk.TclError, AttributeError) as e:
            logging.error("Error closing current tab: %s", e)

    def _show_loading_indicator(self, parent: tk.Widget, message: str) -> tk.Label:
        """Show a loading indicator label in the parent widget."""
        loading_label = tk.Label(
            parent, text=f"🔄 {message}...", font=("Arial", 12), fg="gray"
        )
        loading_label.pack(expand=True)
        parent.update()
        return loading_label

    def _hide_loading_indicator(self, loading_widget: tk.Widget) -> None:
        """Hide the loading indicator"""
        try:
            loading_widget.destroy()
        except tk.TclError:
            pass  # Widget already destroyed

    def open_curve_fitting_tab(self) -> None:
        """Open a new curve fitting tab"""
        if self.tab_manager:
            self.tab_manager.open_curve_fitting_tab()

    def open_uncertainty_calc_tab(self) -> None:
        """Open uncertainty calculator tab"""
        if self.tab_manager:
            self.tab_manager.open_uncertainty_calc_tab()

    def switch_language(self, new_language: str) -> None:
        """Switch the application language."""
        if new_language in ["pt", "en"] and new_language != self.language:
            self.language = new_language
            # Update the dropdown to reflect the change
            if hasattr(self, "lang_var") and self.lang_var is not None:
                self.lang_var.set("Português" if new_language == "pt" else "English")
            self.update_ui_language()

    def on_tab_changed(
        self, event: Optional[Any] = None
    ) -> None:  # pylint: disable=unused-argument
        """Handle tab changed event"""
        if self.notebook is None or not self.tab_manager:
            return
        self.tab_manager.handle_tab_changed()

    def on_close(self) -> None:
        """Handle application close"""
        try:
            # Clean up resources
            if self.tab_manager:
                # TabManager has no cleanup_all_tabs; skip or implement if needed
                pass
            # Clean up matplotlib figures to prevent memory leaks
            try:
                import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel

                plt.close("all")
            except Exception as e:  # pylint: disable=broad-except
                logging.debug("Error closing matplotlib figures: %s", e)
            # Stop the main loop and destroy the window
            self.root.quit()
            self.root.destroy()
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error during application close: %s", e)
            try:
                show_error(
                    get_string("main_app", "error", self.language),
                    get_string("main_app", "close_error", self.language),
                )
            except Exception:
                show_error("Error", str(e))
        finally:
            # Wait a short time to allow graceful shutdown, then force exit if still running
            def force_exit_later():
                import time as _time  # pylint: disable=import-outside-toplevel, reimported

                _time.sleep(1.0)  # Give time for graceful shutdown
                # If process is still alive, force exit
                os._exit(0)

            threading.Thread(target=force_exit_later, daemon=True).start()

    def run(self) -> None:
        """Start the application"""
        # Maximize window immediately for fastest startup
        try:
            # First ensure window is in normal state
            self.root.wm_state("normal")
            self.root.update_idletasks()
            self._immediate_maximize()
        except Exception as e:
            logging.warning("Could not maximize window immediately: %s", e)
        self.root.mainloop()

    def _maximize_with_geometry(self, reason: str) -> None:
        """Fallback maximization using geometry calculation"""
        logging.info("Using geometry maximization: %s", reason)
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Platform-specific taskbar/dock space calculations
        system = platform.system()
        if system == "Darwin":  # macOS
            # Account for macOS menu bar (~25px) and dock (variable, ~60-80px)
            window_width = screen_width - 4
            window_height = screen_height - 90  # Menu bar + dock space
            x_pos, y_pos = 0, 25  # Start below menu bar
        elif system == "Linux":
            # Account for various Linux panels (typically top/bottom, ~30-50px each)
            window_width = screen_width - 4
            window_height = screen_height - 80  # Space for panels
            x_pos, y_pos = 0, 0
        else:  # Windows and others
            # Account for Windows taskbar (~40px)
            window_width = screen_width - 4
            window_height = screen_height - 74  # Taskbar + title bar
            x_pos, y_pos = 0, 0
        geometry_string = f"{window_width}x{window_height}+{x_pos}+{y_pos}"
        logging.info("Setting geometry: %s", geometry_string)
        self.root.geometry(geometry_string)

    def _immediate_maximize(self) -> None:
        """Immediately maximize the window without centering (fallback method)"""
        system = platform.system()
        try:
            if system == "Windows":
                self.root.after(100, lambda: self.root.wm_state("zoomed"))
                logging.info("Window set to maximized state (Windows zoomed)")
            elif system == "Darwin":  # macOS
                try:
                    self.root.wm_state("zoomed")
                    logging.info("Window maximized using zoomed state (macOS)")
                except tk.TclError:
                    self.root.wm_attributes("-fullscreen", False)
                    self.root.wm_attributes("-zoomed", True)
                    logging.info("Window maximized using attributes (macOS)")
            elif system == "Linux":
                try:
                    self.root.wm_attributes("-zoomed", True)
                    logging.info("Window maximized using -zoomed attribute (Linux)")
                except tk.TclError:
                    try:
                        self.root.wm_state("zoomed")
                        logging.info("Window maximized using zoomed state (Linux)")
                    except tk.TclError:
                        self._maximize_with_geometry("Linux fallback")
            else:
                try:
                    self.root.wm_state("zoomed")
                    logging.info("Window maximized using zoomed state (%s)", system)
                except tk.TclError:
                    self._maximize_with_geometry(f"{system} fallback")
        except Exception as e:
            logging.warning("Could not maximize window: %s", e)
            self._maximize_with_geometry("Exception fallback")

    def setup_home_tab(self):
        """Set up the home tab with welcome content"""
        welcome_frame = ttk.Frame(self.home_tab)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = ttk.Frame(welcome_frame)
        header_frame.pack(pady=(30, 10))

        app_name_label = ttk.Label(
            header_frame, text="AnaFis", font=("Segoe UI", 24, "bold")
        )
        app_name_label.pack(side=tk.LEFT)

        version_label = ttk.Label(
            header_frame,
            text=f"v{__version__}",
            font=("Segoe UI", 12),
            foreground="#888",
        )
        version_label.pack(side=tk.LEFT, padx=(5, 0), pady=(10, 0))

        description = ttk.Label(
            welcome_frame,
            text=get_string("main_app", "app_title", self.language),
            font=("Segoe UI", 14),
        )
        description.pack(pady=(0, 30))

        button_frame = ttk.Frame(welcome_frame)
        button_frame.pack(pady=20)

        curve_btn = ttk.Button(
            button_frame,
            text=get_string("main_app", "curve_fitting", self.language),
            command=self.open_curve_fitting_tab,
            width=25,
        )
        curve_btn.pack(pady=10)

        uncertainty_btn = ttk.Button(
            button_frame,
            text=get_string("main_app", "uncertainty_calc", self.language),
            command=self.open_uncertainty_calc_tab,
            width=25,
        )
        uncertainty_btn.pack(pady=10)

        settings_btn = ttk.Button(
            button_frame,
            text=get_string("main_app", "settings", self.language),
            command=self.open_settings_dialog,
            width=25,
        )
        settings_btn.pack(pady=10)

    def open_settings_dialog(self):
        """Open settings dialog to configure user preferences"""
        # Create and show settings dialog
        dialog = SettingsDialog(
            self.root, self.language, callback=self.on_settings_changed
        )
        self.root.wait_window(dialog.top)
    def on_settings_changed(self, updated_settings: Dict[str, Any]) -> None:
        """Handle when settings are changed

        Args:
            updated_settings: Dictionary of settings that were updated
        """
        # Check if language was changed
        if "language" in updated_settings:
            self.language = updated_settings["language"]
            self.update_ui_language()

        # Apply other settings as needed

    def initialize_utilities(
        self,
        progress_callback: "Optional[Callable[[int, str], None]]" = None,  # pylint: disable=unused-argument
    ) -> None:
        """Initialize the utility modules for the application."""
        from app_files.utils.update_checker import (
            update_checker,
        )  # pylint: disable=import-outside-toplevel

        update_checker.initialize()

        # Initialize theme manager with default TTK themes
        from app_files.utils.theme_manager import (
            theme_manager,
        )  # pylint: disable=import-outside-toplevel

        theme_manager.initialize(self.root)

        # Apply user's preferred theme (or default)
        preferred_theme = user_preferences.get_preference("theme", "default")
        theme_manager.apply_theme(preferred_theme)

        # No progress bar updates here; handled in run.py
