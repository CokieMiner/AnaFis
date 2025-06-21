"""Settings dialog for AnaFis application"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import showinfo, showerror, showwarning  # type: ignore
from tkinter import filedialog
import os
import logging
from typing import Optional, Callable, Dict, Any, Type, Union, List
import platform
import subprocess

from app_files.utils.constants import TRANSLATIONS
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
        tooltip_bg = theme_manager.get_adaptive_color('background')
        self.tooltip_window.configure(bg=tooltip_bg)
        
        # Create tooltip label with theme-appropriate colors
        tooltip_fg = theme_manager.get_adaptive_color('foreground')
        tooltip_fg = theme_manager.get_adaptive_color('foreground')
        
        label = ttk.Label(self.tooltip_window, text=self.text, wraplength=250,
                         background=tooltip_bg, foreground=tooltip_fg, relief="solid", borderwidth=1)
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
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
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
        self._current_status_state: str = 'not_checked'  # 'error', 'success', 'warning', 'not_checked'
          # Create toplevel window
        self.top = tk.Toplevel(parent)
        self.top.title(TRANSLATIONS[language]['settings'])
        self.top.geometry("600x500")
        self.top.resizable(True, True)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Configure theme-appropriate background for the window
        bg_color = theme_manager.get_adaptive_color('background')
        self.top.configure(bg=bg_color)
        
        # Register for theme change callbacks to update colors automatically
        theme_manager.register_color_update_callback(self._update_colors)

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
        
        self.notebook.add(self.general_tab, text=TRANSLATIONS[language]['general'])
        self.notebook.add(self.interface_tab, text=TRANSLATIONS[language]['interface'])
        self.notebook.add(self.export_tab, text=TRANSLATIONS[language]['export'])
        self.notebook.add(self.updates_tab, text=TRANSLATIONS[language]['updates'])

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
            text=TRANSLATIONS[language]['save'],
            command=self.save_settings
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text=TRANSLATIONS[language]['cancel'],
            command=self.top.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Reset button
        reset_btn = ttk.Button(
            button_frame,
            text=TRANSLATIONS[language]['reset'],
            command=self.reset_to_defaults
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    def setup_general_tab(self):
        """Set up the general settings tab"""
        frame = ttk.LabelFrame(
            self.general_tab,
            text=TRANSLATIONS[self.language]['general_settings']
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Language selection
        ttk.Label(frame, text=TRANSLATIONS[self.language]['language_label']).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)

        self.language_var = tk.StringVar(value=user_preferences.get_language())
        language_combo = ttk.Combobox(
            frame,
            textvariable=self.language_var,
            values=[f"{code} - {user_preferences.get_language_name(code)}"
                   for code in user_preferences.get_available_languages()],
            state="readonly",
            width=20
        )
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        language_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.mark_setting_changed('language',
                                              self.language_var.get().split(' - ')[0])
        )
        
        # Check for updates
        self.check_updates_var = tk.BooleanVar(
            value=user_preferences.get_preference('check_updates', True)
        )
        check_updates_check = ttk.Checkbutton(
            frame,
            text=TRANSLATIONS[self.language]['check_updates'],
            variable=self.check_updates_var
        )
        check_updates_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        check_updates_check.configure(
            command=lambda: self.mark_setting_changed('check_updates',
                                                    self.check_updates_var.get())
        )
    def setup_interface_tab(self):
        """Set up the interface settings tab"""
        frame = ttk.LabelFrame(
            self.interface_tab,
            text=TRANSLATIONS[self.language]['interface_settings']
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Theme selection
        ttk.Label(frame, text=TRANSLATIONS[self.language]['theme']).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)

        theme_frame = ttk.Frame(frame)
        theme_frame.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        current_theme = theme_manager.get_current_theme()
        self.theme_var = tk.StringVar(value=current_theme)
        
        theme_names = theme_manager.get_available_themes()

        self.theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=theme_names,
            state="readonly",
            width=20
        )
        self.theme_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        self.theme_dropdown.bind('<<ComboboxSelected>>', self.on_theme_changed)

        # Reload themes button
        reload_button = ttk.Button(theme_frame, text="↻", width=3,
                                  command=self._refresh_themes)
        reload_button.pack(side=tk.LEFT, padx=5)

        # Open custom themes directory button
        folder_button = ttk.Button(theme_frame, text="📁", width=3,
                                  command=self._open_themes_directory)
        folder_button.pack(side=tk.LEFT, padx=5)

        # Add tooltips to buttons
        ToolTip(self.theme_dropdown, TRANSLATIONS[self.language]['tooltip_theme_dropdown'])
        ToolTip(reload_button, TRANSLATIONS[self.language]['tooltip_reload_themes'])
        ToolTip(folder_button, TRANSLATIONS[self.language]['tooltip_open_themes_dir'])

        # Theme info display
        info_frame = ttk.Frame(frame)
        info_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=10)
        ttk.Label(info_frame, text=TRANSLATIONS[self.language]['current_theme']).pack(side=tk.LEFT)
        
        # Use theme-appropriate color for current theme label
        info_color = theme_manager.get_adaptive_color('text_info')
        self.current_theme_label = ttk.Label(info_frame, text=current_theme, foreground=info_color)
        self.current_theme_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Theme statistics
        stats_frame = ttk.Frame(frame)
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)
        theme_count = len(theme_names)
        self.theme_count_label = ttk.Label(stats_frame, text=f"{TRANSLATIONS[self.language]['available_themes']} {theme_count}")
        self.theme_count_label.pack(side=tk.LEFT)
        
    def on_theme_changed(self, event: Optional[Any] = None) -> None:
        """Handle theme dropdown selection change"""
        theme_name = self.theme_var.get()
        
        # Preview the theme globally without saving the preference yet
        theme_manager.apply_theme(theme_name, save_preference=False)
        
        # Mark the setting as changed so it can be saved if the user clicks "Save"
        self.mark_setting_changed('theme', theme_name)
        
        # Update the label in the settings dialog
        if hasattr(self, 'current_theme_label'):
            self.current_theme_label.config(text=theme_name)
        
    def setup_export_tab(self):
        """Set up the export settings tab"""
        frame = ttk.LabelFrame(
            self.export_tab,
            text=TRANSLATIONS[self.language]['export_settings']
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)        # Graph DPI
        ttk.Label(frame, text=TRANSLATIONS[self.language]['graph_dpi']).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.graph_dpi_var = tk.StringVar(
            value=str(user_preferences.get_preference('graph_dpi', 100))
        )
        graph_dpi_entry = ttk.Entry(frame, textvariable=self.graph_dpi_var, width=5)
        graph_dpi_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        graph_dpi_entry.bind(
            "<FocusOut>",
            lambda e: self.validate_and_mark('graph_dpi', self.graph_dpi_var.get(), int)
        )
        
        # Export format
        ttk.Label(frame, text=TRANSLATIONS[self.language]['export_format']).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5
        )

        # Get format code from preferences
        format_code = user_preferences.get_preference('export_format', 'png')
        # Convert to display name
        format_display_name = self._get_format_display_name(format_code)
        
        self.export_format_var = tk.StringVar(value=format_display_name)
        
        # Create a list of format names from translations
        format_values = [
            self._get_format_display_name('png'),
            self._get_format_display_name('jpg'),
            self._get_format_display_name('svg'),
            self._get_format_display_name('pdf')
        ]
        
        export_format_combo = ttk.Combobox(
            frame,
            textvariable=self.export_format_var,
            values=format_values,
            state="readonly",
            width=20
        )
        export_format_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        export_format_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self._on_format_selected(e)
        )
          # Last export directory
        ttk.Label(frame, text=TRANSLATIONS[self.language]['last_export_directory']).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=5)

        self.export_dir_var = tk.StringVar(
            value=user_preferences.get_preference('last_export_directory', '')
        )
        export_dir_entry = ttk.Entry(frame, textvariable=self.export_dir_var, width=30)
        export_dir_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        export_dir_entry.bind(
            "<FocusOut>",
            lambda e: self.mark_setting_changed('last_export_directory',
                                               self.export_dir_var.get())
        )
          # Browse button
        browse_btn = ttk.Button(
            frame,
            text=TRANSLATIONS[self.language]['browse'],
            command=self.browse_export_directory
        )
        browse_btn.grid(row=2, column=2, padx=5, pady=5)

    def setup_updates_tab(self):
        """Set up the updates tab"""
        
        frame = ttk.LabelFrame(
            self.updates_tab,
            text=TRANSLATIONS[self.language].get('update_settings', 'Updates')
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Current version section
        version_frame = ttk.Frame(frame)
        version_frame.pack(fill=tk.X, padx=10, pady=5)
        
        from app_files import __version__
        ttk.Label(version_frame, text=TRANSLATIONS[self.language].get('current_version', 'Current Version:')).pack(side=tk.LEFT)
        ttk.Label(version_frame, text=f"v{__version__}", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT, padx=(5, 0))
        
        # Update check section
        check_frame = ttk.Frame(frame)
        check_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Check button and status on same row
        self.check_btn = ttk.Button(
            check_frame,
            text=TRANSLATIONS[self.language].get('check_for_updates', 'Check for Updates'),
            command=self.check_for_updates
        )
        self.check_btn.pack(side=tk.LEFT)
        
        # Compact status indicator (always visible, fixed size)
        text_muted = theme_manager.get_adaptive_color('text_muted')
        self.status_indicator = ttk.Label(
            check_frame, 
            text="●", 
            foreground=text_muted,
            font=('TkDefaultFont', 12)
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(10, 5))
        
        self.status_text = ttk.Label(
            check_frame,
            text=TRANSLATIONS[self.language].get('not_checked', 'Not checked'),
            foreground=text_muted
        )
        self.status_text.pack(side=tk.LEFT)
        
        # Last check info (always visible, fixed size)
        text_muted = theme_manager.get_adaptive_color('text_muted')
        self.last_check_label = ttk.Label(
            frame, 
            text=TRANSLATIONS[self.language].get('never_checked', 'Never checked for updates'),
            foreground=text_muted,
            font=('TkDefaultFont', 8)
        )
        self.last_check_label.pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        # Download section (always visible but conditionally enabled)
        download_frame = ttk.Frame(frame)
        download_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.download_btn = ttk.Button(
            download_frame,
            text=TRANSLATIONS[self.language].get('download_update', 'Download Update'),
            command=self.open_download_page,
            state='disabled'  # Start disabled
        )
        self.download_btn.pack(side=tk.LEFT)
        
        # Use theme-appropriate color for download info
        info_color = theme_manager.get_adaptive_color('text_info')
        self.download_info = ttk.Label(
            download_frame,
            text="",
            foreground=info_color,
            cursor="hand2"
        )
        self.download_info.pack(side=tk.LEFT, padx=(10, 0))
        self.download_info.bind("<Button-1>", lambda e: self.open_download_page())
        
        # Auto-check for updates
        auto_check_frame = ttk.Frame(frame)
        auto_check_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.auto_check_var = tk.BooleanVar(
            value=user_preferences.get_preference('auto_check_updates', True)
        )
        auto_check = ttk.Checkbutton(
            auto_check_frame,
            text=TRANSLATIONS[self.language].get('auto_check_updates', 'Automatically check for updates'),
            variable=self.auto_check_var,
            command=lambda: self.mark_setting_changed('auto_check_updates', 
                                                   self.auto_check_var.get())
        )
        auto_check.pack(side=tk.LEFT)
        
        # Initialize update status display
        self.update_update_status()
    
    def check_for_updates(self):
        """Check for updates and update the UI"""
        from app_files.utils.update_checker import update_checker
        
        # Disable check button and show checking status
        self.check_btn.config(state='disabled')
        
        # Use consistent warning color for checking status
        current_bg = theme_manager.get_adaptive_color('background')
        is_dark_bg = self._is_dark_background(current_bg)
        warning_color = "#FFD700" if is_dark_bg else "#FF8C00"
        
        self.status_indicator.config(foreground=warning_color)
        self.status_text.config(
            text=TRANSLATIONS[self.language].get('checking_for_updates', 'Checking...'),
            foreground=warning_color
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
                self.top.after(0, lambda: self.check_btn.config(state='normal'))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def update_update_status(self):
        """Update the update status display with stable, non-flickering UI"""
        from app_files.utils.update_checker import update_checker
        
        # Get theme-appropriate colors
        text_muted = theme_manager.get_adaptive_color('text_muted')
        
        # Define consistent semantic colors that work in both light and dark themes
        # These will stay red/green regardless of theme changes
        current_bg = theme_manager.get_adaptive_color('background')
        is_dark_bg = self._is_dark_background(current_bg)
        
        if is_dark_bg:
            # Dark theme - use lighter, more visible colors
            error_color = "#FF6B6B"    # Light red for dark backgrounds
            success_color = "#90EE90"  # Light green for dark backgrounds
        else:
            # Light theme - use darker, more readable colors
            error_color = "#DC143C"    # Dark red for light backgrounds
            success_color = "#228B22"  # Forest green for light backgrounds
        
        # Update last check time (always show)
        if update_checker.last_check_time:
            check_time_str = update_checker.last_check_time.strftime("%d/%m/%Y %H:%M")
            self.last_check_label.config(
                text=f"{TRANSLATIONS[self.language].get('last_checked', 'Last checked')}: {check_time_str}",
                foreground=text_muted
            )
        else:
            self.last_check_label.config(
                text=TRANSLATIONS[self.language].get('never_checked', 'Never checked for updates'),
                foreground=text_muted
            )
        
        # Update status based on check results using consistent semantic colors
        if update_checker.error:
            # Error state - use consistent red color
            self._current_status_state = 'error'
            self.status_indicator.config(foreground=error_color)
            self.status_text.config(
                text=TRANSLATIONS[self.language].get('check_failed', 'Check failed'),
                foreground=error_color
            )
            self.download_btn.config(state='disabled')
            self.download_info.config(text="")
            
        elif update_checker.update_available and update_checker.latest_version:
            # Update available - use consistent green color
            self._current_status_state = 'success'
            self.status_indicator.config(foreground=success_color)
            self.status_text.config(
                text=TRANSLATIONS[self.language].get('update_available', 'Update available'),
                foreground=success_color
            )
            self.download_btn.config(state='normal')
            self.download_info.config(text=f"v{update_checker.latest_version}")
            
        elif update_checker.latest_version:
            # Up to date - use consistent green color
            self._current_status_state = 'success'
            self.status_indicator.config(foreground=success_color)
            self.status_text.config(
                text=TRANSLATIONS[self.language].get('up_to_date', 'Up to date'),
                foreground=success_color
            )
            self.download_btn.config(state='disabled')
            self.download_info.config(text="")
            
        else:
            # Not checked - use theme-appropriate muted color
            self._current_status_state = 'not_checked'
            self.status_indicator.config(foreground=text_muted)
            self.status_text.config(
                text=TRANSLATIONS[self.language].get('not_checked', 'Not checked'),
                foreground=text_muted
            )
            self.download_btn.config(state='disabled')
            self.download_info.config(text="")
    
    def _is_dark_background(self, color_str: str) -> bool:
        """
        Determine if a background color is dark
        Returns True if dark, False if light
        """
        try:
            if color_str.startswith('#'):
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
            return color_str.lower() in ['black', 'dark', 'gray', 'grey']
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
            # Update main dialog background
            bg_color = theme_manager.get_adaptive_color('background')
            self.top.configure(bg=bg_color)
            
            # Update updates tab colors specifically
            self._update_updates_tab_colors()
            
            # Note: TTK widgets will automatically update with the theme
            # Only Toplevel and Text widgets need manual updates
            logging.debug("Settings dialog colors updated for theme change")
        except Exception as e:
            logging.warning(f"Failed to update settings dialog colors: {e}")
    
    def _update_updates_tab_colors(self) -> None:
        """Update colors for the updates tab widgets"""
        try:
            # Update download info color to use theme-appropriate info color
            if hasattr(self, 'download_info') and self.download_info.winfo_exists():
                info_color = theme_manager.get_adaptive_color('text_info')
                self.download_info.config(foreground=info_color)
            
            # Update last check label to use theme-appropriate text color
            if hasattr(self, 'last_check_label') and self.last_check_label.winfo_exists():
                text_color = theme_manager.get_adaptive_color('text_muted')
                self.last_check_label.config(foreground=text_color)
            
            # Always refresh the status colors to ensure they use consistent semantic colors
            # The update_update_status method now uses consistent red/green colors
            if hasattr(self, 'update_update_status'):
                self.update_update_status()
                
            # Schedule another status color update after a short delay to ensure
            # our colors aren't overridden by TTK theme updates
            if hasattr(self, 'top') and self.top.winfo_exists():
                self.top.after(50, self._preserve_status_colors)
                
        except Exception as e:
            logging.debug(f"Error updating updates tab colors: {e}")
    
    def _preserve_status_colors(self) -> None:
        """Ensure status colors are preserved after theme changes"""
        try:
            if hasattr(self, 'update_update_status'):
                self.update_update_status()
        except Exception as e:
            logging.debug(f"Error preserving status colors: {e}")
    def validate_and_mark(self, key: str, value: str, value_type: Type[Union[int, str]]) -> None:
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
                if key == 'decimal_places' and (typed_value < 0 or typed_value > 15):
                    raise ValueError("Decimal places must be between 0 and 15")
                if key == 'graph_dpi' and (typed_value < 50 or typed_value > 300):
                    raise ValueError("Graph DPI must be between 50 and 300")
            else:
                typed_value = value_type(value)

            self.mark_setting_changed(key, typed_value)
        except ValueError as e:
            messagebox.showerror(  # type: ignore[misc]
                TRANSLATIONS[self.language]['error'],
                str(e)
            )
            # Reset to current value
            if key == 'graph_dpi':
                self.graph_dpi_var.set(
                    str(user_preferences.get_preference('graph_dpi', 100))
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
            title=TRANSLATIONS[self.language]['select_directory']
        )
        
        # Update if directory selected
        if selected_dir:
            self.export_dir_var.set(selected_dir)
            self.mark_setting_changed(
                'last_export_directory', selected_dir
            )

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
            self.top.destroy()
        else:
            # Some settings failed validation/saving
            error_message = TRANSLATIONS[self.language]['save_error_specific'] \
                            + ": " + ", ".join(failed_settings_keys)
            messagebox.showerror(  # type: ignore[misc]
                TRANSLATIONS[self.language]['error'],
                error_message
            )
            # Do not close the dialog, allow user to correct

    def reset_to_defaults(self):
        """Reset all settings to default values"""
        if messagebox.askyesno(  # type: ignore[misc]
            TRANSLATIONS[self.language]['confirm'],
            TRANSLATIONS[self.language]['reset_confirm']
        ):
            # Reset to defaults
            user_preferences.reset_to_defaults()

            # Close and reopen dialog to refresh
            self.top.destroy()
            SettingsDialog(self.parent, self.language, self.callback)

    def _get_theme_display_name(self, theme_code: str) -> str:
        """Get the display name for a theme code using the translation system."""
        if theme_code in ['light', 'dark', 'auto'] and f'theme_{theme_code}' in TRANSLATIONS[self.language]:
            return TRANSLATIONS[self.language][f'theme_{theme_code}']
        # Fallback to code if translation not found
        return theme_code

    def _on_theme_selected(self, event: Any) -> None:
        """Handle theme selection from the dropdown, converting from display name to code."""
        # Ignore the event parameter
        selected_theme_name = self.theme_var.get()
        
        # Convert display name back to theme code
        theme_code = self._get_theme_code_from_name(selected_theme_name)
        
        # Mark the setting as changed
        self.mark_setting_changed('theme', theme_code)
        
    def _get_theme_code_from_name(self, theme_name: str) -> str:
        """Convert a theme display name to its code."""
        # Check each possible theme
        if theme_name == TRANSLATIONS[self.language]['theme_light']:
            return 'light'
        elif theme_name == TRANSLATIONS[self.language]['theme_dark']:
            return 'dark'
        elif theme_name == TRANSLATIONS[self.language]['theme_auto']:
            return 'auto'
        # Default to light if unknown
        return 'light'
    
    def _get_format_display_name(self, format_code: str) -> str:
        """Get the display name for a file format code using the translation system."""
        if format_code in ['png', 'jpg', 'svg', 'pdf'] and f'format_{format_code}' in TRANSLATIONS[self.language]:
            return TRANSLATIONS[self.language][f'format_{format_code}']
        # Fallback to code if translation not found
        return format_code
        
    def _on_format_selected(self, event: Any) -> None:
        """Handle format selection from the dropdown, converting from display name to code."""
        # Ignore the event parameter
        selected_format_name = self.export_format_var.get()
        
        # Convert display name back to format code
        format_code = self._get_format_code_from_name(selected_format_name)
        
        # Mark the setting as changed
        self.mark_setting_changed('export_format', format_code)
        
    def _get_format_code_from_name(self, format_name: str) -> str:
        """Convert a format display name to its code."""
        # Check each possible format
        if format_name == TRANSLATIONS[self.language]['format_png']:
            return 'png'
        elif format_name == TRANSLATIONS[self.language]['format_jpg']:
            return 'jpg'
        elif format_name == TRANSLATIONS[self.language]['format_svg']:
            return 'svg'
        elif format_name == TRANSLATIONS[self.language]['format_pdf']:
            return 'pdf'
        # Default to png if unknown
        return 'png'
    
    def _refresh_themes(self) -> None:
        """Refresh the theme list"""
        # Refresh themes by calling reload_themes
        new_theme_count = theme_manager.reload_themes()
        
        # Get the updated list of theme names
        theme_names = theme_manager.get_available_themes()

        # Update dropdown values
        self.theme_dropdown['values'] = theme_names
        
        # Update theme count label
        if hasattr(self, 'theme_count_label'):
            self.theme_count_label.config(text=f"Available themes: {new_theme_count}")

        # Show message
        showinfo("Themes Refreshed",
                 f"Theme list updated. Found {new_theme_count} themes.")
        

    def _open_themes_directory(self) -> None:
        """Open the custom themes directory in file explorer"""
        try:
            themes_dir = theme_manager.get_themes_directory()
            self._open_directory(themes_dir)
            
            # Show info message about custom themes
            showinfo("Custom Themes Directory", #type: ignore
                              f"Opened custom themes directory:\n{themes_dir}\n\n"
                              "Place your .tcl theme files here and click the reload button to use them.")
            
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


