"""Settings dialog for AnaFis application"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os

from app_files.utils.constants import TRANSLATIONS
from app_files.utils.user_preferences import user_preferences

class SettingsDialog:
    """Dialog for configuring application settings"""

    def __init__(self, parent, language, callback=None):
        """Initialize settings dialog

        Args:
            parent: Parent window
            language: Current language
            callback: Function to call when settings change
        """
        self.parent = parent
        self.language = language
        self.callback = callback
        self.modified_settings = {}
          # Create toplevel window
        self.top = tk.Toplevel(parent)
        self.top.title(TRANSLATIONS[language]['settings'])
        self.top.geometry("600x500")
        self.top.resizable(True, True)
        self.top.transient(parent)
        self.top.grab_set()

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
        self.data_tab = ttk.Frame(self.notebook)
        self.export_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.general_tab, text=TRANSLATIONS[language]['general'])
        self.notebook.add(self.interface_tab, text=TRANSLATIONS[language]['interface'])
        self.notebook.add(self.data_tab, text=TRANSLATIONS[language]['data'])
        self.notebook.add(self.export_tab, text=TRANSLATIONS[language]['export'])

        # Setup tab contents
        self.setup_general_tab()
        self.setup_interface_tab()
        self.setup_data_tab()
        self.setup_export_tab()

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
          # Auto-save
        self.autosave_var = tk.BooleanVar(value=user_preferences.get_preference('auto_save', True))
        autosave_check = ttk.Checkbutton(
            frame,
            text=TRANSLATIONS[self.language]['auto_save'],
            variable=self.autosave_var
        )
        autosave_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        autosave_check.configure(
            command=lambda: self.mark_setting_changed('auto_save',
                                                     self.autosave_var.get())
        )
          # Auto-backup
        self.autobackup_var = tk.BooleanVar(
            value=user_preferences.get_preference('auto_backup', True)
        )
        autobackup_check = ttk.Checkbutton(
            frame,
            text=TRANSLATIONS[self.language]['auto_backup'],
            variable=self.autobackup_var
        )
        autobackup_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        autobackup_check.configure(
            command=lambda: self.mark_setting_changed('auto_backup',
                                                     self.autobackup_var.get())
        )
          # Backup interval
        ttk.Label(frame, text=TRANSLATIONS[self.language]['backup_interval']).grid(
            row=3, column=0, sticky=tk.W, padx=10, pady=5)

        self.backup_interval_var = tk.StringVar(
            value=str(user_preferences.get_preference('backup_interval_minutes', 30))
        )
        backup_interval_entry = ttk.Entry(frame, textvariable=self.backup_interval_var, width=5)
        backup_interval_entry.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        backup_interval_entry.bind(
            "<FocusOut>",
            lambda e: self.validate_and_mark('backup_interval_minutes',
                                           self.backup_interval_var.get(), int)
        )        # Check for updates
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

        self.theme_var = tk.StringVar(value=user_preferences.get_preference('theme', 'light'))
        theme_combo = ttk.Combobox(
            frame,
            textvariable=self.theme_var,
            values=["light", "dark", "auto"],
            state="readonly",
            width=10
        )
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        theme_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.mark_setting_changed('theme', self.theme_var.get())
        )        # Font size
        ttk.Label(frame, text=TRANSLATIONS[self.language]['font_size']).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.font_size_var = tk.StringVar(
            value=str(user_preferences.get_preference('font_size', 12))
        )
        font_size_entry = ttk.Entry(frame, textvariable=self.font_size_var, width=5)
        font_size_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        font_size_entry.bind(
            "<FocusOut>",            lambda e: self.validate_and_mark(
                'font_size', self.font_size_var.get(), int
            )
        )        # Show tooltips
        self.tooltips_var = tk.BooleanVar(
            value=user_preferences.get_preference('show_tooltips', True)
        )
        tooltips_check = ttk.Checkbutton(
            frame,
            text=TRANSLATIONS[self.language]['show_tooltips'],
            variable=self.tooltips_var
        )
        tooltips_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        tooltips_check.configure(
            command=lambda: self.mark_setting_changed('show_tooltips',
                                                     self.tooltips_var.get())
        )

        # Remember window size
        self.remember_size_var = tk.BooleanVar(
            value=user_preferences.get_preference('remember_window_size', True)
        )
        remember_size_check = ttk.Checkbutton(
            frame,
            text=TRANSLATIONS[self.language]['remember_window_size'],
            variable=self.remember_size_var
        )
        remember_size_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        remember_size_check.configure(
            command=lambda: self.mark_setting_changed('remember_window_size',
                                                     self.remember_size_var.get())
        )

        # Show welcome screen
        self.welcome_screen_var = tk.BooleanVar(
            value=user_preferences.get_preference('show_welcome_screen', True)
        )
        welcome_screen_check = ttk.Checkbutton(
            frame,
            text=TRANSLATIONS[self.language]['show_welcome_screen'],
            variable=self.welcome_screen_var
        )
        welcome_screen_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        welcome_screen_check.configure(
            command=lambda: self.mark_setting_changed('show_welcome_screen',
                                                     self.welcome_screen_var.get())
        )
    def setup_data_tab(self):
        """Set up the data settings tab"""
        frame = ttk.LabelFrame(
            self.data_tab,
            text=TRANSLATIONS[self.language]['data_settings']
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Decimal places
        ttk.Label(frame, text=TRANSLATIONS[self.language]['decimal_places']).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)

        self.decimal_places_var = tk.StringVar(
            value=str(user_preferences.get_preference('decimal_places', 4))
        )
        decimal_places_entry = ttk.Entry(
            frame, textvariable=self.decimal_places_var, width=5
        )
        decimal_places_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        decimal_places_entry.bind(
            "<FocusOut>",
            lambda e: self.validate_and_mark('decimal_places',
                                           self.decimal_places_var.get(), int)
        )        # Advanced mode
        self.advanced_mode_var = tk.BooleanVar(
            value=user_preferences.get_preference('advanced_mode', False)
        )
        advanced_mode_check = ttk.Checkbutton(
            frame,
            text=TRANSLATIONS[self.language]['advanced_mode'],
            variable=self.advanced_mode_var
        )
        advanced_mode_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        advanced_mode_check.configure(            command=lambda: self.mark_setting_changed(
                'advanced_mode', self.advanced_mode_var.get()
            )
        )

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
        )        # Export format
        ttk.Label(frame, text=TRANSLATIONS[self.language]['export_format']).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.export_format_var = tk.StringVar(
            value=user_preferences.get_preference('export_format', 'png')
        )
        export_format_combo = ttk.Combobox(
            frame,
            textvariable=self.export_format_var,
            values=["png", "jpg", "svg", "pdf"],
            state="readonly",
            width=5
        )
        export_format_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        export_format_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.mark_setting_changed('export_format',
                                              self.export_format_var.get())
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

    def mark_setting_changed(self, key, value):
        """Mark a setting as changed

        Args:
            key: Setting key
            value: New value
        """
        self.modified_settings[key] = value
    def validate_and_mark(self, key, value, value_type):
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
                if key == 'font_size' and (typed_value < 8 or typed_value > 72):
                    raise ValueError("Font size must be between 8 and 72")
                if key == 'decimal_places' and (typed_value < 0 or typed_value > 15):
                    raise ValueError("Decimal places must be between 0 and 15")
                if key == 'graph_dpi' and (typed_value < 50 or typed_value > 300):
                    raise ValueError("Graph DPI must be between 50 and 300")
                if key == 'backup_interval_minutes' and (typed_value < 1 or typed_value > 1440):
                    raise ValueError("Backup interval must be between 1 and 1440 minutes")
            else:
                typed_value = value_type(value)

            self.mark_setting_changed(key, typed_value)
        except ValueError as e:
            messagebox.showerror(
                TRANSLATIONS[self.language]['error'],
                str(e)
            )
            # Reset to current value
            if key == 'font_size':
                self.font_size_var.set(
                    str(user_preferences.get_preference('font_size', 12))
                )

            elif key == 'decimal_places':
                self.decimal_places_var.set(
                    str(user_preferences.get_preference('decimal_places', 4))
                )

            elif key == 'graph_dpi':
                self.graph_dpi_var.set(
                    str(user_preferences.get_preference('graph_dpi', 100))
                )

            elif key == 'backup_interval_minutes':
                self.backup_interval_var.set(
                    str(user_preferences.get_preference('backup_interval_minutes', 30))
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
        )        # Update if directory selected
        if selected_dir:
            self.export_dir_var.set(selected_dir)
            self.mark_setting_changed(
                'last_export_directory', selected_dir
            )

    def save_settings(self):
        """Save all modified settings"""
        try:
            # First validate all numeric settings
            if 'font_size' in self.modified_settings:
                self.validate_and_mark(
                    'font_size', str(self.modified_settings['font_size']), int
                )

            if 'decimal_places' in self.modified_settings:
                self.validate_and_mark(
                    'decimal_places', str(self.modified_settings['decimal_places']), int
                )

            if 'graph_dpi' in self.modified_settings:
                self.validate_and_mark('graph_dpi', str(self.modified_settings['graph_dpi']), int)

            if 'backup_interval_minutes' in self.modified_settings:
                self.validate_and_mark(
                    'backup_interval_minutes',
                    str(self.modified_settings['backup_interval_minutes']),
                    int
                )

            # Save all modified settings
            for key, value in self.modified_settings.items():
                user_preferences.set_preference(key, value)

            # Call callback if provided
            if self.callback and self.modified_settings:
                self.callback(self.modified_settings)

            # Close dialog
            self.top.destroy()

        except (ValueError, OSError, KeyError) as e:
            messagebox.showerror(
                TRANSLATIONS[self.language]['error'],
                f"{TRANSLATIONS[self.language]['save_error']}: {str(e)}"
            )
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        if messagebox.askyesno(
            TRANSLATIONS[self.language]['confirm'],
            TRANSLATIONS[self.language]['reset_confirm']
        ):
            # Reset to defaults
            user_preferences.reset_to_defaults()

            # Close and reopen dialog to refresh
            self.top.destroy()
            SettingsDialog(self.parent, self.language, self.callback)
