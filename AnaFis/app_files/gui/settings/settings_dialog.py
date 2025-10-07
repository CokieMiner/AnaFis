"""Settings dialog for AnaFis application"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import showinfo, showerror, showwarning
from tkinter import filedialog
import os
import logging
from typing import Optional, Callable, Dict, Any, Type, Union, List
import platform
import subprocess

from app_files.utils.translations.api import get_string
from app_files.utils.user_preferences import user_preferences
from app_files.utils.theme_manager import theme_manager


class ToolTip:
    """Simple tooltip implementation for tkinter widgets"""

    def __init__(self, widget: tk.Widget, text: str):
        """Initialize tooltip for a widget

        Args:
            widget: The widget to show tooltip for
            text: Tooltip text
        """
        self.widget = widget
        self.text = text
        self.tooltip_window: Optional[tk.Toplevel] = None

        # Bind events
        self.widget.bind("<Enter>", self._show)
        self.widget.bind("<Leave>", self._hide)
        self.widget.bind("<Motion>", self._move)

    def _show(self, event: Optional[tk.Event] = None) -> None:
        """Show the tooltip"""
        if self.tooltip_window:
            return

        # Get position
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25

        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Configure tooltip window background
        tooltip_bg = theme_manager.get_adaptive_color("background")
        self.tooltip_window.configure(bg=tooltip_bg)

        # Create tooltip label with theme-appropriate colors
        tooltip_fg = theme_manager.get_adaptive_color("foreground")
        tooltip_fg = theme_manager.get_adaptive_color("foreground")

        label = ttk.Label(
            self.tooltip_window,
            text=self.text,
            wraplength=250,
            background=tooltip_bg,
            foreground=tooltip_fg,
            relief="solid",
            borderwidth=1,
        )
        label.pack(padx=2, pady=2)

    def _hide(self, event: Optional[tk.Event] = None) -> None:
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def _move(self, event: Optional[tk.Event] = None) -> None:
        """Move the tooltip"""
        if self.tooltip_window and event:
            x = event.x_root + 15
            y = event.y_root + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")


class SettingsDialog:
    """Dialog for configuring application settings"""

    def __init__(
        self,
        parent: tk.Tk,
        language: str,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """Initialize settings dialog

        Args:
            parent: Parent window
            language: Current language
            callback: Function to call when settings change
        """
        self.parent = parent
        self.language = language
        self.callback = callback
        self.modified_settings: Dict[str, Any] = {}

        # Track current update status for color persistence
        self._current_status_state: str = (
            "not_checked"  # 'error', 'success', 'warning', 'not_checked'
        )
        # Create toplevel window
        self.top = tk.Toplevel(parent)
        self.top.title(get_string("settings", "settings", language))
        self.top.geometry("600x500")
        self.top.resizable(True, True)
        self.top.transient(parent)
        self.top.grab_set()

        # Configure theme-appropriate background for the window
        bg_color = theme_manager.get_adaptive_color("background")
        self.top.configure(bg=bg_color)

        # Register for theme changes
        theme_manager.register_color_callback(self._update_colors)

        # Bind cleanup to window close
        self.top.protocol("WM_DELETE_WINDOW", self._on_close)

        # Center the window
        window_width = 600
        window_height = 500
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create notebook for tab organization
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.general_tab = ttk.Frame(self.notebook)
        self.interface_tab = ttk.Frame(self.notebook)
        self.export_tab = ttk.Frame(self.notebook)
        self.updates_tab = ttk.Frame(self.notebook)

        self.notebook.add(
            self.general_tab, text=get_string("settings", "general", language)
        )
        self.notebook.add(
            self.interface_tab, text=get_string("settings", "interface", language)
        )
        self.notebook.add(
            self.export_tab, text=get_string("settings", "export", language)
        )
        self.notebook.add(
            self.updates_tab, text=get_string("settings", "updates", language)
        )

        # Setup tab contents
        self.setup_general_tab()
        self.setup_interface_tab()
        self.setup_export_tab()
        self.setup_updates_tab()

        # Bottom buttons
        button_frame = ttk.Frame(self.top)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        # Save button
        save_btn = ttk.Button(
            button_frame,
            text=get_string("settings", "save", language),
            command=self.save_settings,
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text=get_string("settings", "cancel", language),
            command=self._on_close,
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Reset button
        reset_btn = ttk.Button(
            button_frame,
            text=get_string("settings", "reset", language),
            command=self.reset_to_defaults,
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

    def setup_general_tab(self):
        """Set up the general settings tab"""
        frame = ttk.LabelFrame(
            self.general_tab,
            text=get_string("settings", "general_settings", self.language),
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Language selection
        ttk.Label(
            frame, text=get_string("settings", "language_label", self.language)
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        self.language_var = tk.StringVar(
            self.top, value=user_preferences.get_language()
        )
        language_combo = ttk.Combobox(
            frame,
            textvariable=self.language_var,
            values=["pt", "en"],
            state="readonly",
            width=10,
        )
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        language_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.mark_setting_changed("language", self.language_var.get()),
        )

        # Decimal places
        ttk.Label(
            frame, text=get_string("settings", "decimal_places", self.language)
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

        self.decimal_places_var = tk.StringVar(
            self.top, value=str(user_preferences.get_preference("decimal_places", 3))
        )
        decimal_places_entry = ttk.Entry(
            frame, textvariable=self.decimal_places_var, width=5
        )
        decimal_places_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        decimal_places_entry.bind(
            "<FocusOut>",
            lambda e: self.validate_and_mark(
                "decimal_places", self.decimal_places_var.get(), int
            ),
        )

        # Check for updates
        self.check_updates_var = tk.BooleanVar(
            self.top, value=user_preferences.get_preference("check_updates", True)
        )
        check_updates_check = ttk.Checkbutton(
            frame,
            text=get_string("settings", "check_updates", self.language),
            variable=self.check_updates_var,
        )
        check_updates_check.grid(
            row=4, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5
        )
        check_updates_check.configure(
            command=lambda: self.mark_setting_changed(
                "check_updates", self.check_updates_var.get()
            )
        )

    def setup_interface_tab(self):
        """Set up the interface settings tab"""
        frame = ttk.LabelFrame(
            self.interface_tab,
            text=get_string("settings", "interface_settings", self.language),
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Theme selection
        ttk.Label(frame, text=get_string("settings", "theme", self.language)).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5
        )

        theme_frame = ttk.Frame(frame)
        theme_frame.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        # Get theme names for dropdown
        theme_infos = theme_manager.get_available_themes()
        theme_names = [theme.display_name for theme in theme_infos]
        current_theme_name = theme_manager.get_current_theme() or "default"

        # Find the display name for the current theme
        current_theme_display = current_theme_name.title()  # Default fallback
        for theme_info in theme_infos:
            if theme_info.name == current_theme_name:
                current_theme_display = theme_info.display_name
                break

        # Create theme dropdown with display name
        self.theme_var = tk.StringVar(self.top, value=current_theme_display)
        self.theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=theme_names,
            state="readonly",
            width=20,
        )
        self.theme_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        self.theme_dropdown.bind("<<ComboboxSelected>>", self.on_theme_changed)

        # Reload themes button
        reload_button = ttk.Button(
            theme_frame, text="↻", width=3, command=self._refresh_themes
        )
        reload_button.pack(side=tk.LEFT, padx=5)

        # Open custom themes directory button
        folder_button = ttk.Button(
            theme_frame, text="📁", width=3, command=self._open_themes_directory
        )
        folder_button.pack(side=tk.LEFT, padx=5)

        # Add tooltips to buttons
        ToolTip(
            self.theme_dropdown,
            get_string("settings", "tooltip_theme_dropdown", self.language),
        )
        ToolTip(
            reload_button,
            get_string("settings", "tooltip_reload_themes", self.language),
        )
        ToolTip(
            folder_button,
            get_string("settings", "tooltip_open_themes_dir", self.language),
        )

        # Theme info display
        info_frame = ttk.Frame(frame)
        info_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=10)
        ttk.Label(
            info_frame, text=get_string("settings", "current_theme", self.language)
        ).pack(side=tk.LEFT)

        # Use theme-appropriate color for current theme label
        info_color = theme_manager.get_adaptive_color("text_info")
        self.current_theme_label = ttk.Label(
            info_frame, text=current_theme_display, foreground=info_color
        )
        self.current_theme_label.pack(side=tk.LEFT, padx=(5, 0))

        # Theme statistics
        stats_frame = ttk.Frame(frame)
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)
        theme_count = len(theme_names)
        self.theme_count_label = ttk.Label(
            stats_frame,
            text=f"{get_string('settings', 'available_themes', self.language)} {theme_count}",
        )
        self.theme_count_label.pack(side=tk.LEFT)

    def on_theme_changed(self, event: Optional[Any] = None) -> None:
        """Handle theme dropdown selection change"""
        theme_display_name = self.theme_var.get()

        # Convert display name back to internal name
        theme_infos = theme_manager.get_available_themes()
        theme_internal_name = theme_display_name.lower()  # Default fallback
        for theme_info in theme_infos:
            if theme_info.display_name == theme_display_name:
                theme_internal_name = theme_info.name
                break

        # Preview the theme globally without saving the preference yet
        theme_manager.apply_theme(theme_internal_name)

        # Mark the setting as changed so it can be saved if the user clicks "Save"
        self.mark_setting_changed("theme", theme_internal_name)

        # Update the label in the settings dialog
        if hasattr(self, "current_theme_label"):
            self.current_theme_label.config(text=theme_display_name)

    def setup_export_tab(self):
        """Set up the export settings tab"""
        frame = ttk.LabelFrame(
            self.export_tab,
            text=get_string("settings", "export_settings", self.language),
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Graph DPI
        ttk.Label(frame, text=get_string("settings", "graph_dpi", self.language)).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.graph_dpi_var = tk.StringVar(
            self.top, value=str(user_preferences.get_preference("graph_dpi", 100))
        )
        graph_dpi_entry = ttk.Entry(frame, textvariable=self.graph_dpi_var, width=5)
        graph_dpi_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        graph_dpi_entry.bind(
            "<FocusOut>",
            lambda e: self.validate_and_mark(
                "graph_dpi", self.graph_dpi_var.get(), int
            ),
        )

        # Export format
        ttk.Label(
            frame, text=get_string("settings", "export_format", self.language)
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

        # Get format code from preferences
        format_code = user_preferences.get_preference("export_format", "png")
        # Convert to display name
        format_display_name = self._get_format_display_name(format_code)

        self.export_format_var = tk.StringVar(self.top, value=format_display_name)

        # Create a list of format names from translations
        format_values = [
            self._get_format_display_name("png"),
            self._get_format_display_name("jpg"),
            self._get_format_display_name("svg"),
            self._get_format_display_name("pdf"),
        ]

        export_format_combo = ttk.Combobox(
            frame,
            textvariable=self.export_format_var,
            values=format_values,
            state="readonly",
            width=20,
        )
        export_format_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        export_format_combo.bind(
            "<<ComboboxSelected>>", lambda e: self._on_format_selected(e)
        )
        # Last export directory
        ttk.Label(
            frame, text=get_string("settings", "last_export_directory", self.language)
        ).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)

        self.export_dir_var = tk.StringVar(
            self.top, value=user_preferences.get_preference("last_export_directory", "")
        )
        export_dir_entry = ttk.Entry(frame, textvariable=self.export_dir_var, width=30)
        export_dir_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        export_dir_entry.bind(
            "<FocusOut>",
            lambda e: self.mark_setting_changed(
                "last_export_directory", self.export_dir_var.get()
            ),
        )
        # Browse button
        browse_btn = ttk.Button(
            frame,
            text=get_string("settings", "browse", self.language),
            command=self.browse_export_directory,
        )
        browse_btn.grid(row=2, column=2, padx=5, pady=5)

    def setup_updates_tab(self):
        """Set up the updates tab"""

        frame = ttk.LabelFrame(
            self.updates_tab,
            text=get_string("settings", "update_settings", self.language),
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Current version section
        version_frame = ttk.Frame(frame)
        version_frame.pack(fill=tk.X, padx=10, pady=5)

        from app_files import __version__

        ttk.Label(
            version_frame, text=get_string("settings", "current_version", self.language)
        ).pack(side=tk.LEFT)
        ttk.Label(
            version_frame, text=f"v{__version__}", font=("TkDefaultFont", 9, "bold")
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Update check section
        check_frame = ttk.Frame(frame)
        check_frame.pack(fill=tk.X, padx=10, pady=10)

        # Check button and status on same row
        self.check_btn = ttk.Button(
            check_frame,
            text=get_string("settings", "check_for_updates", self.language),
            command=self.check_for_updates,
        )
        self.check_btn.pack(side=tk.LEFT)

        # Compact status indicator (always visible, fixed size)
        text_muted = theme_manager.get_adaptive_color("text_muted")
        self.status_indicator = ttk.Label(
            check_frame, text="●", foreground=text_muted, font=("TkDefaultFont", 12)
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(10, 5))

        self.status_text = ttk.Label(
            check_frame,
            text=get_string("settings", "not_checked", self.language),
            foreground=text_muted,
        )
        self.status_text.pack(side=tk.LEFT)

        # Last check info (always visible, fixed size)
        text_muted = theme_manager.get_adaptive_color("text_muted")
        self.last_check_label = ttk.Label(
            frame,
            text=get_string("settings", "never_checked", self.language),
            foreground=text_muted,
            font=("TkDefaultFont", 8),
        )
        self.last_check_label.pack(anchor=tk.W, padx=10, pady=(5, 0))

        # Download section (always visible but conditionally enabled)
        download_frame = ttk.Frame(frame)
        download_frame.pack(fill=tk.X, padx=10, pady=10)

        self.download_btn = ttk.Button(
            download_frame,
            text=get_string("settings", "download_update", self.language),
            command=self.open_download_page,
            state="disabled",  # Start disabled
        )
        self.download_btn.pack(side=tk.LEFT)

        # Use theme-appropriate color for download info
        info_color = theme_manager.get_adaptive_color("text_info")
        self.download_info = ttk.Label(
            download_frame, text="", foreground=info_color, cursor="hand2"
        )
        self.download_info.pack(side=tk.LEFT, padx=(10, 0))
        self.download_info.bind("<Button-1>", lambda e: self.open_download_page())

        # Auto-check for updates
        auto_check_frame = ttk.Frame(frame)
        auto_check_frame.pack(fill=tk.X, padx=10, pady=10)

        self.auto_check_var = tk.BooleanVar(
            self.top, value=user_preferences.get_preference("auto_check_updates", True)
        )
        auto_check = ttk.Checkbutton(
            auto_check_frame,
            text=get_string("settings", "auto_check_updates", self.language),
            variable=self.auto_check_var,
            command=lambda: self.mark_setting_changed(
                "auto_check_updates", self.auto_check_var.get()
            ),
        )
        auto_check.pack(side=tk.LEFT)

        # Initialize update status display
        self.update_update_status()

    def check_for_updates(self):
        """Check for updates and update the UI"""
        from app_files.utils.update_checker import update_checker

        # Disable check button and show checking status
        self.check_btn.config(state="disabled")

        # Use consistent warning color for checking status
        current_bg = theme_manager.get_adaptive_color("background")
        is_dark_bg = self._is_dark_background(current_bg)
        warning_color = "#FFD700" if is_dark_bg else "#FF8C00"

        self.status_indicator.config(foreground=warning_color)
        self.status_text.config(
            text=get_string("settings", "checking_for_updates", self.language),
            foreground=warning_color,
        )
        self.top.update_idletasks()

        # Run the update check in a separate thread to avoid blocking UI
        import threading

        def check_thread():
            try:
                update_checker.force_check_updates()
                # Schedule UI update on main thread
                self.top.after(0, self.update_update_status)
            except Exception as e:
                logging.error(f"Error checking for updates: {e}")
                self.top.after(0, self.update_update_status)
            finally:
                # Re-enable check button
                self.top.after(0, lambda: self.check_btn.config(state="normal"))

        threading.Thread(target=check_thread, daemon=True).start()

    def update_update_status(self):
        """Update the update status display with stable, non-flickering UI"""
        from app_files.utils.update_checker import update_checker

        # Get theme-appropriate colors
        text_muted = theme_manager.get_adaptive_color("text_muted")

        # Define consistent semantic colors that work in both light and dark themes
        # These will stay red/green regardless of theme changes
        current_bg = theme_manager.get_adaptive_color("background")
        is_dark_bg = self._is_dark_background(current_bg)

        if is_dark_bg:
            # Dark theme - use lighter, more visible colors
            error_color = "#FF6B6B"  # Light red for dark backgrounds
            success_color = "#90EE90"  # Light green for dark backgrounds
        else:
            # Light theme - use darker, more readable colors
            error_color = "#DC143C"  # Dark red for light backgrounds
            success_color = "#228B22"  # Forest green for light backgrounds

        # Update last check time (always show)
        if update_checker.last_check_time:
            check_time_str = update_checker.last_check_time.strftime("%d/%m/%Y %H:%M")
            self.last_check_label.config(
                text=f"{get_string('settings', 'last_checked', self.language)}: {check_time_str}",
                foreground=text_muted,
            )
        else:
            self.last_check_label.config(
                text=get_string("settings", "never_checked", self.language),
                foreground=text_muted,
            )

        # Update status based on check results using consistent semantic colors
        if update_checker.error:
            # Error state - use consistent red color
            self._current_status_state = "error"
            self.status_indicator.config(foreground=error_color)
            self.status_text.config(
                text=get_string("settings", "check_failed", self.language),
                foreground=error_color,
            )
            self.download_btn.config(state="disabled")
            self.download_info.config(text="")

        elif update_checker.update_available and update_checker.latest_version:
            # Update available - use consistent green color
            self._current_status_state = "success"
            self.status_indicator.config(foreground=success_color)
            self.status_text.config(
                text=get_string("settings", "update_available", self.language),
                foreground=success_color,
            )
            self.download_btn.config(state="normal")
            self.download_info.config(text=f"v{update_checker.latest_version}")

        elif update_checker.latest_version:
            # Up to date - use consistent green color
            self._current_status_state = "success"
            self.status_indicator.config(foreground=success_color)
            self.status_text.config(
                text=get_string("settings", "up_to_date", self.language),
                foreground=success_color,
            )
            self.download_btn.config(state="disabled")
            self.download_info.config(text="")

        else:
            # Not checked - use theme-appropriate muted color
            self._current_status_state = "not_checked"
            self.status_indicator.config(foreground=text_muted)
            self.status_text.config(
                text=get_string("settings", "not_checked", self.language),
                foreground=text_muted,
            )
            self.download_btn.config(state="disabled")
            self.download_info.config(text="")

    def _is_dark_background(self, color_str: str) -> bool:
        """
        Determine if a background color is dark
        Returns True if dark, False if light
        """
        try:
            if color_str.startswith("#"):
                # Convert hex to RGB
                hex_color = color_str[1:]
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    # Calculate luminance
                    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                    return luminance < 0.5
            # Fallback for non-hex colors
            return color_str.lower() in ["black", "dark", "gray", "grey"]
        except:
            return False

    def open_download_page(self):
        """Open the download page in the default browser"""
        from app_files.utils.update_checker import update_checker
        import webbrowser

        if update_checker.release_url:
            webbrowser.open(update_checker.release_url)

    def mark_setting_changed(self, key: str, value: Any) -> None:
        """Mark a setting as changed

        Args:
            key: Setting key
            value: New value
        """
        self.modified_settings[key] = value

    def _update_colors(self) -> None:
        """Update colors when theme changes"""
        try:
            # Check if window still exists before updating
            if not hasattr(self, "top") or not self.top.winfo_exists():
                return

            # Update main dialog background
            bg_color = theme_manager.get_adaptive_color("background")
            self.top.configure(bg=bg_color)

            # Update updates tab colors specifically
            self._update_updates_tab_colors()

            # Note: TTK widgets will automatically update with the theme
            # Only Toplevel and Text widgets need manual updates
            logging.debug("Settings dialog colors updated for theme change")
        except Exception as e:
            logging.warning(f"Failed to update settings dialog colors: {e}")

    def _on_close(self) -> None:
        """Cleanup when dialog is closed"""
        try:
            # Unregister color callback to prevent errors after window is destroyed
            theme_manager.unregister_color_callback(self._update_colors)
        except Exception as e:
            logging.debug(f"Error unregistering color callback: {e}")
        finally:
            # Destroy the window
            self.top.destroy()

    def _update_updates_tab_colors(self) -> None:
        """Update colors for the updates tab widgets"""
        try:
            # Update download info color to use theme-appropriate info color
            if hasattr(self, "download_info") and self.download_info.winfo_exists():
                info_color = theme_manager.get_adaptive_color("text_info")
                self.download_info.config(foreground=info_color)

            # Update last check label to use theme-appropriate text color
            if (
                hasattr(self, "last_check_label")
                and self.last_check_label.winfo_exists()
            ):
                text_color = theme_manager.get_adaptive_color("text_muted")
                self.last_check_label.config(foreground=text_color)

            # Always refresh the status colors to ensure they use consistent semantic colors
            # The update_update_status method now uses consistent red/green colors
            if hasattr(self, "update_update_status"):
                self.update_update_status()

            # Schedule another status color update after a short delay to ensure
            # our colors aren't overridden by TTK theme updates
            if hasattr(self, "top") and self.top.winfo_exists():
                self.top.after(50, self._preserve_status_colors)

        except Exception as e:
            logging.debug(f"Error updating updates tab colors: {e}")

    def _preserve_status_colors(self) -> None:
        """Ensure status colors are preserved after theme changes"""
        try:
            if hasattr(self, "update_update_status"):
                self.update_update_status()
        except Exception as e:
            logging.debug(f"Error preserving status colors: {e}")

    def validate_and_mark(
        self, key: str, value: str, value_type: Type[Union[int, str]]
    ) -> None:
        """Validate a value and mark as changed if valid

        Args:
            key: Setting key
            value: Value to validate
            value_type: Type to convert to
        """
        try:
            # For numeric types, validate range
            if value_type == int:
                typed_value = int(value)
                if key == "decimal_places" and (typed_value < 0 or typed_value > 15):
                    raise ValueError("Decimal places must be between 0 and 15")
                if key == "graph_dpi" and (typed_value < 50 or typed_value > 300):
                    raise ValueError("Graph DPI must be between 50 and 300")
            else:
                typed_value = value_type(value)

            self.mark_setting_changed(key, typed_value)
        except ValueError as e:
            messagebox.showerror(get_string("settings", "error", self.language), str(e))
            # Reset to current value
            if key == "graph_dpi":
                self.graph_dpi_var.set(
                    str(user_preferences.get_preference("graph_dpi", 100))
                )

    def browse_export_directory(self):
        """Open directory browser for export directory"""
        # Get current directory or default to home
        current_dir = self.export_dir_var.get()
        if not current_dir or not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")

        # Open directory dialog
        selected_dir = filedialog.askdirectory(
            initialdir=current_dir,
            title=get_string("settings", "select_directory", self.language),
        )

        # Update if directory selected
        if selected_dir:
            self.export_dir_var.set(selected_dir)
            self.mark_setting_changed("last_export_directory", selected_dir)

    def save_settings(self):
        """Save all modified settings"""
        all_settings_saved = True
        failed_settings_keys: List[str] = []

        # Attempt to save all modified settings
        # user_preferences.set_preference will now handle validation internally
        for key, value in self.modified_settings.items():
            if not user_preferences.set_preference(key, value):
                all_settings_saved = False
                failed_settings_keys.append(key)

        if all_settings_saved:
            # Call callback if provided and settings were actually modified and saved
            if self.callback and self.modified_settings:
                self.callback(self.modified_settings)

            # Close dialog only if all settings saved successfully
            self._on_close()
        else:
            # Some settings failed validation/saving
            error_message = (
                get_string("settings", "save_error_specific", self.language)
                + ": "
                + ", ".join(failed_settings_keys)
            )
            messagebox.showerror(
                get_string("settings", "error", self.language), error_message
            )
            # Do not close the dialog, allow user to correct

    def reset_to_defaults(self):
        """Reset all settings to default values"""
        if messagebox.askyesno(
            get_string("settings", "confirm", self.language),
            get_string("settings", "reset_confirm", self.language),
        ):
            # Reset to defaults
            user_preferences.reset_to_defaults()

            # Close and reopen dialog to refresh
            # First unregister callback before destroying
            theme_manager.unregister_color_callback(self._update_colors)
            self.top.destroy()
            SettingsDialog(self.parent, self.language, self.callback)

    def _get_theme_display_name(self, theme_code: str) -> str:
        """Get the display name for a theme code using the translation system."""
        if theme_code in [
            "light",
            "dark",
            "auto",
        ] and f"theme_{theme_code}" in get_string(
            "settings", "translations", self.language
        ):
            return get_string("settings", f"theme_{theme_code}", self.language)
        # Fallback to code if translation not found
        return theme_code

    def _on_theme_selected(self, event: Any) -> None:
        """Handle theme selection from the dropdown, converting from display name to code."""
        # Ignore the event parameter
        selected_theme_name = self.theme_var.get()

        # Convert display name back to theme code
        theme_code = self._get_theme_code_from_name(selected_theme_name)

        # Mark the setting as changed
        self.mark_setting_changed("theme", theme_code)

    def _get_theme_code_from_name(self, theme_name: str) -> str:
        """Convert a theme display name to its code."""
        # Check each possible theme
        if theme_name == get_string("settings", "theme_light", self.language):
            return "light"
        elif theme_name == get_string("settings", "theme_dark", self.language):
            return "dark"
        elif theme_name == get_string("settings", "theme_auto", self.language):
            return "auto"
        # Default to light if unknown
        return "light"

    def _get_format_display_name(self, format_code: str) -> str:
        """Get the display name for a file format code using the translation system."""
        if format_code in [
            "png",
            "jpg",
            "svg",
            "pdf",
        ] and f"format_{format_code}" in get_string(
            "settings", "translations", self.language
        ):
            return get_string("settings", f"format_{format_code}", self.language)
        # Fallback to code if translation not found
        return format_code

    def _on_format_selected(self, event: Any) -> None:
        """Handle format selection from the dropdown, converting from display name to code."""
        # Ignore the event parameter
        selected_format_name = self.export_format_var.get()

        # Convert display name back to format code
        format_code = self._get_format_code_from_name(selected_format_name)

        # Mark the setting as changed
        self.mark_setting_changed("export_format", format_code)

    def _get_format_code_from_name(self, format_name: str) -> str:
        """Convert a format display name to its code."""
        # Check each possible format
        if format_name == get_string("settings", "format_png", self.language):
            return "png"
        elif format_name == get_string("settings", "format_jpg", self.language):
            return "jpg"
        elif format_name == get_string("settings", "format_svg", self.language):
            return "svg"
        elif format_name == get_string("settings", "format_pdf", self.language):
            return "pdf"
        # Default to png if unknown
        return "png"

    def _refresh_themes(self) -> None:
        """Refresh the theme list"""
        # Clear cache and reload themes
        theme_manager.clear_cache()

        # Reinitialize theme manager to reload themes
        if theme_manager.root:
            theme_manager._load_all_themes()

        # Get the updated list of theme names
        theme_infos = theme_manager.get_available_themes()
        theme_names = [theme.display_name for theme in theme_infos]

        # Update dropdown values
        self.theme_dropdown["values"] = theme_names

        # Update theme count label
        if hasattr(self, "theme_count_label"):
            self.theme_count_label.config(text=f"Available themes: {len(theme_names)}")

        # Show message
        showinfo(
            "Themes Refreshed", f"Theme list updated. Found {len(theme_names)} themes."
        )

    def _open_themes_directory(self) -> None:
        """Open the custom themes directory in file explorer"""
        try:
            themes_dir = theme_manager.get_themes_directory()
            self._open_directory(themes_dir)

            # Show info message about custom themes
            showinfo(
                "Custom Themes Directory",
                f"Opened custom themes directory:\n{themes_dir}\n\n"
                "Place your .tcl theme files here and click the reload button to use them.",
            )

        except Exception as e:
            # Log error (logging is imported at module level)
            logging.error(f"Error opening themes directory: {e}")
            showerror("Error", f"Failed to open themes directory: {e}")

    def _open_directory(self, directory_path: str) -> None:
        """Open a directory in the file explorer"""
        try:
            # Make sure the directory exists
            os.makedirs(directory_path, exist_ok=True)

            # Open the directory using the appropriate command for the platform
            if platform.system() == "Windows":
                os.startfile(directory_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", directory_path])
            else:  # Linux
                subprocess.run(["xdg-open", directory_path])

        except Exception as e:
            # Log error (logging is imported at module level)
            logging.error(f"Error opening directory: {e}")
            showerror("Error", f"Failed to open directory: {e}")
