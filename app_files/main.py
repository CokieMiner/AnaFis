"""Main application module"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging
import os
from typing import Any, Dict, List, Optional, Protocol, Tuple, TypedDict, Union, cast

# Import the version from app_files package
from app_files import __version__

from app_files.utils.constants import TRANSLATIONS
from app_files.utils.user_preferences import user_preferences
from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
from app_files.gui.incerteza.calculo_incertezas_gui import CalculoIncertezasFrame
from app_files.gui.settings.settings_dialog import SettingsDialog

# Type alias for language
LanguageType = Union[str, Any]

# Define a Protocol for common tab instance methods
class TabInstanceProtocol(Protocol):
    """Defines the interface for tab instances managed by AplicativoUnificado."""
    def switch_language(self, language: str) -> None:
        """Switches the language of the tab's UI elements."""
        ...

    def cleanup(self) -> None:
        """Performs cleanup operations when the tab is closed."""
        ...

    def on_tab_activated(self) -> None:
        """
        Called when the tab becomes active.
        Implementations can be a no-op (e.g., 'pass') if no specific action is needed.
        """
        ...

# Define a TypedDict for the structure of tab data in self.open_tabs
class TabData(TypedDict):
    widget: ttk.Frame
    instance: TabInstanceProtocol

class AplicativoUnificado:
    """Main application class with tabbed interface"""

    def __init__(self) -> None:
        self.root = tk.Tk()
        # Load language from user preferences - explicitly type as str
        self.language: str = user_preferences.get_preference('language', 'pt')

        # Initialize UI component attributes with proper typing
        self.lang_label: Optional[ttk.Label] = None
        self.lang_var: Optional[tk.StringVar] = None
        self.lang_dropdown: Optional[ttk.Combobox] = None
        self.toolbar_frame: ttk.Frame
        self.notebook: ttk.Notebook
        self.home_tab: ttk.Frame
        self.tab_menu: tk.Menu
        self.icon: Optional[tk.PhotoImage] = None        
        # Use the TabData TypedDict for open_tabs
        self.open_tabs: Dict[str, Union[TabData, str]] = {}

        # Set application icon
        self.set_app_icon()

        # Set title
        self.root.title(TRANSLATIONS[self.language]['app_title'])

        # Setup main UI components (creates toolbar_frame and notebook)
        self.setup_toolbar()
        self.setup_notebook()

        # Create tab context menu after notebook is created
        self.tab_menu = tk.Menu(self.root, tearoff=0)
        self.tab_menu.add_command(
            label="Close",
            command=self.close_current_tab
        )

        # Setup main UI components
        self.setup_toolbar()
        # Configure root layout
        self.setup_notebook()
        
        self.root.geometry("1200x800")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_app_icon(self):
        """Set the application icon from utils/icon.png"""
        try:
            # Get the path to the icon file in the utils folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            utils_dir = os.path.join(current_dir, 'utils')
            icon_path = os.path.join(utils_dir, 'icon.png')

            # Check if the icon file exists
            if not os.path.exists(icon_path):
                logging.warning("Icon file not found at: %s", icon_path)
                return

            # Create a PhotoImage from the icon file
            icon = tk.PhotoImage(file=icon_path)

            # Set as application icon
            self.root.iconphoto(True, icon)

            # Store the icon to prevent garbage collection
            self.icon = icon

        except (OSError, tk.TclError) as e:
            logging.error("Error setting application icon: %s", e)

    def setup_toolbar(self):
        """Set up toolbar with application controls"""
        # Create toolbar frame
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)        # Configure toolbar columns
        self.toolbar_frame.columnconfigure(0, weight=0)  
        self.toolbar_frame.columnconfigure(1, weight=0)  
        self.toolbar_frame.columnconfigure(2, weight=1)  
        self.toolbar_frame.columnconfigure(3, weight=0)
        # Add buttons to toolbar
        curve_fit_btn = ttk.Button(
            self.toolbar_frame,
            text=TRANSLATIONS[self.language]['curve_fitting'],
            command=self.open_curve_fitting_tab)
        curve_fit_btn.grid(row=0, column=0, padx=5, sticky="w")

        uncertainty_btn = ttk.Button(
            self.toolbar_frame,
            text=TRANSLATIONS[self.language]['uncertainty_calc'],
            command=self.open_uncertainty_calc_tab)
        uncertainty_btn.grid(row=0, column=1, padx=5, sticky="w")
        # Add language selector to toolbar
        self.setup_language_selector()

    def setup_language_selector(self):
        """Set up language selector in toolbar"""
        # Create language frame
        lang_frame = ttk.Frame(self.toolbar_frame)
        lang_frame.grid(row=0, column=3, padx=5, sticky="e")
        # Language label
        self.lang_label = ttk.Label(
            lang_frame, text=TRANSLATIONS[self.language]['language_label'])
        self.lang_label.grid(row=0, column=0, padx=(0, 5))        # Language dropdown
        self.lang_var = tk.StringVar(
            value="Português" if self.language == 'pt' else "English")
        self.lang_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["Português", "English"],
            state="readonly",
            width=10
        )
        self.lang_dropdown.grid(row=0, column=1)
        self.lang_dropdown.bind('<<ComboboxSelected>>', self.on_language_changed)

    def on_language_changed(self, event: Optional[Any] = None) -> None:
        """Handle language dropdown selection change"""
        # Underscore prefix indicates intentionally unused parameter
        _ = event

        if self.lang_var is None:
            return
        selected = self.lang_var.get()
        new_language = 'pt' if selected == "Português" else 'en'

        if new_language != self.language:
            self.language = new_language
            # Save the language preference
            user_preferences.set_preference('language', new_language)
            self.update_ui_language()

    def update_ui_language(self):
        """Update all UI elements to reflect the new language"""
        # Update window title
        self.root.title(TRANSLATIONS[self.language]['app_title'])

        # Update toolbar buttons
        self._update_toolbar_buttons()

        # Update language label
        if hasattr(self, 'lang_label') and self.lang_label is not None:
            self.lang_label.configure(
                text=TRANSLATIONS[self.language]['language_label'])

        # Update all open tabs
        self._update_open_tab_instances()
        # Update tab texts in notebook
        self._update_notebook_tabs()
        # Refresh home tab to update all text
        if hasattr(self, 'home_tab'):
            for widget in self.home_tab.winfo_children():
                widget.destroy()
            self.setup_home_tab()

    def _update_toolbar_buttons(self):
        """Update toolbar button texts to current language"""
        for widget in self.toolbar_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                current_text = widget.cget('text')
                if current_text in [
                    TRANSLATIONS['pt']['curve_fitting'],
                    TRANSLATIONS['en']['curve_fitting']
                ]:
                    widget.configure(
                        text=TRANSLATIONS[self.language]['curve_fitting'])
                elif current_text in [
                    TRANSLATIONS['pt']['uncertainty_calc'],
                    TRANSLATIONS['en']['uncertainty_calc']                ]:
                    widget.configure(
                        text=TRANSLATIONS[self.language]['uncertainty_calc'])

    def _update_notebook_tabs(self):
        """Update notebook tab texts to current language"""
        _tab_ids_tuple = self.notebook.tabs() # type: ignore[misc]
        # Cast to actual expected type to help type checker for subsequent operations
        tab_ids_raw = cast(Tuple[str, ...], _tab_ids_tuple)
        tabs_list: List[str] = list(tab_ids_raw) if tab_ids_raw else [] # No more type: ignore[arg-type] or map(str,...)
        for i, _ in enumerate(tabs_list):
            # Get tab text
            tab_text = str(self.notebook.tab(i, 'text')) # type: ignore[misc]
            if tab_text in [TRANSLATIONS['pt']['curve_fitting'],
                            TRANSLATIONS['en']['curve_fitting']]:
                self.notebook.tab( # type: ignore[misc]
                    i, text=TRANSLATIONS[self.language]['curve_fitting']) 
            elif tab_text in [TRANSLATIONS['pt']['uncertainty_calc'],
                              TRANSLATIONS['en']['uncertainty_calc']]:
                self.notebook.tab( # type: ignore[misc]
                    i, text=TRANSLATIONS[self.language]['uncertainty_calc']) 
            elif tab_text in [TRANSLATIONS['pt']['home'],
                              TRANSLATIONS['en']['home']]:
                self.notebook.tab( # type: ignore[misc]
                    i, text=TRANSLATIONS[self.language]['home']) 

    def _update_open_tab_instances(self):
        """Update all open tab instances to current language"""
        for tab_entry in self.open_tabs.values():
            if isinstance(tab_entry, dict): # Check if it's TabData
                tab_instance = tab_entry.get('instance')
                if tab_instance and hasattr(tab_instance, 'switch_language'):
                    tab_instance.switch_language(self.language)

    def restore_tab_close_buttons(self):
        """Check all tabs and restore close buttons if missing"""
        _tab_ids_tuple = self.notebook.tabs() # type: ignore[misc]
        tab_ids_raw = cast(Tuple[str, ...], _tab_ids_tuple)
        tabs_list: List[str] = list(tab_ids_raw) if tab_ids_raw else [] # No more type: ignore[arg-type] or map(str,...)
        for tab_id_str in tabs_list: 
            tab_frame = self.notebook.nametowidget(tab_id_str) # type: ignore[misc]
            # Check for the dynamically added 'app_close_button' from add_close_button_to_tab
            app_close_button = getattr(tab_frame, 'app_close_button', None)
            if not (app_close_button and app_close_button.winfo_exists()):
                # Ensure tab_frame is a ttk.Frame before passing to add_close_button_to_tab
                if isinstance(tab_frame, ttk.Frame):
                    self.add_close_button_to_tab(tab_frame)
                else:
                    logging.warning(f"Cannot add close button to non-Frame widget: {tab_frame}")

    def setup_notebook(self):
        """Set up the notebook (tabbed interface)"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Add home tab that can't be closed
        self.home_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.home_tab, text=TRANSLATIONS[self.language]['home'])

        # Store reference to home tab
        self.open_tabs['home'] = 'home'  # Special marker for home tab

        # Setup home tab content
        self.setup_home_tab()        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        # Bind right-click event for context menu
        self.notebook.bind("<Button-3>", self.on_tab_right_click)

    def monitor_tabs(self):
        """Periodically check tabs to ensure close buttons are visible"""
        _tab_ids_tuple = self.notebook.tabs() # type: ignore[misc]
        tab_ids_raw = cast(Tuple[str, ...], _tab_ids_tuple)
        tabs_list: List[str] = list(tab_ids_raw) if tab_ids_raw else [] # No more type: ignore[arg-type] or map(str,...)
        for i, tab_id_str in enumerate(tabs_list):
            if i > 0:  # Skip home tab
                tab_frame = self.notebook.nametowidget(tab_id_str) # type: ignore[misc]
                app_close_button = getattr(tab_frame, 'app_close_button', None)
                if not (app_close_button and app_close_button.winfo_exists()):
                    if isinstance(tab_frame, ttk.Frame):
                        self.add_close_button_to_tab(tab_frame)
                    else:
                        logging.warning(f"Monitor: Cannot add close button to non-Frame: {tab_frame}")
        self.root.after(1000, self.monitor_tabs)

    def add_close_button_to_tab(self, tab_main_frame: ttk.Frame) -> ttk.Frame:
        """
        Adds a standardized header with a close button to the given tab_main_frame.
        The tab_main_frame is the widget directly added to the notebook.
        Returns a new frame within tab_main_frame where the actual tab content should be placed.
        """
        # Check if already set up to prevent duplication if called multiple times
        if hasattr(tab_main_frame, 'app_content_container'):
            return getattr(tab_main_frame, 'app_content_container')

        # Header frame for the close button
        # This frame stays at the top and only fills horizontally
        app_header_frame = ttk.Frame(tab_main_frame)
        app_header_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

        app_close_button = ttk.Button(
            app_header_frame,
            text="X",
            width=2,
            command=lambda tmf=tab_main_frame: self.try_close_tab(tmf)
        )
        app_close_button.pack(side=tk.RIGHT, padx=2, pady=2) # Small padding

        # Content container frame where the actual tab module will build its UI
        # This frame fills the rest of the tab_main_frame
        app_content_container = ttk.Frame(tab_main_frame)
        app_content_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Store references on the tab_main_frame itself
        setattr(tab_main_frame, 'app_header_frame', app_header_frame)
        setattr(tab_main_frame, 'app_close_button', app_close_button)
        setattr(tab_main_frame, 'app_content_container', app_content_container)

        return app_content_container

    def try_close_tab(self, tab_frame: tk.Widget) -> None:
        """Try to close a tab by finding its numeric index

        Args:
            tab_frame: The frame of the tab to close
        """
        try:
            _tab_ids_tuple = self.notebook.tabs() # type: ignore[misc]
            tab_ids_raw = cast(Tuple[str, ...], _tab_ids_tuple)
            tabs_list: List[str] = list(tab_ids_raw) if tab_ids_raw else [] # No more type: ignore[arg-type] or map(str,...)
            for i, tab_id_str in enumerate(tabs_list):
                if self.notebook.nametowidget(tab_id_str) == tab_frame: # type: ignore[misc]
                    self.close_tab_at_index(i)
                    return
            logging.warning(f"Could not find tab to close: {tab_frame}")
        except (tk.TclError, AttributeError) as e:
            logging.error("Error finding tab to close: %s", e)

    def close_tab_at_index(self, index: int) -> None:
        """Close a tab at a specific index

        Args:
            index: The index of the tab to close
        """
        try:
            _current_tabs_tuple = self.notebook.tabs() # type: ignore[misc]
            current_tabs_raw = cast(Tuple[str, ...], _current_tabs_tuple)
            current_tabs_list: List[str] = list(current_tabs_raw) if current_tabs_raw else [] # No more type: ignore[arg-type] or map(str,...)
            
            if not current_tabs_list or index >= len(current_tabs_list):
                logging.warning(f"Tab index {index} out of range.")
                return

            tab_to_check_name = current_tabs_list[index]
            widget_to_check = self.notebook.nametowidget(tab_to_check_name) # type: ignore[misc]

            if index == 0 and widget_to_check == self.home_tab:
                return

            tab_widget_to_close = widget_to_check
            
            tab_key_to_delete = None
            instance_to_cleanup = None

            for key, tab_data_entry in self.open_tabs.items():
                if isinstance(tab_data_entry, dict): # Check if it's TabData
                    # Now Pylance knows tab_data_entry is a dict (specifically, TabData compatible)
                    if tab_data_entry.get('widget') == tab_widget_to_close:
                        tab_key_to_delete = key
                        instance_to_cleanup = tab_data_entry.get('instance')
                        break
            
            if instance_to_cleanup and hasattr(instance_to_cleanup, 'cleanup'):
                try:
                    instance_to_cleanup.cleanup()
                except (AttributeError, RuntimeError) as e:
                    logging.error(f"Error in tab cleanup for {tab_key_to_delete}: {e}")

            if tab_key_to_delete:
                del self.open_tabs[tab_key_to_delete]
            else:
                logging.warning(f"Tab at index {index} (widget: {tab_widget_to_close}) not found in open_tabs tracking.")

            self.notebook.forget(index) # type: ignore[misc]
        except (tk.TclError, ValueError, KeyError, IndexError) as e:
            logging.error(f"Error closing tab at index {index}: {e}")

    def on_tab_right_click(self, event: Any) -> None:
        """Show context menu on right-click"""
        try:
            tab_ids_raw = self.notebook.tabs() # type: ignore[misc]
            if not tab_ids_raw: 
                return
            # tabs_list: List[str] = list(map(str, tab_ids_raw)) # Not strictly needed if only using index

            try:
                tab_index = self.notebook.index(f"@{event.x},{event.y}") # type: ignore[misc]
                if isinstance(tab_index, int) and tab_index >= 0:
                    self.notebook.select(tab_index) # type: ignore[misc]
                    if tab_index == 0:
                        return
                else:
                    return # Not a valid tab index
            except tk.TclError:
                return 

            # Display the context menu at cursor position
            self.tab_menu.post(event.x_root, event.y_root)
        except tk.TclError as e:
            logging.debug(f"Tab right-click TclError: {e}")

    def close_current_tab(self):
        """Close the currently selected tab"""
        try:
            selected_tab_path = self.notebook.select() # type: ignore[misc]
            if not selected_tab_path:
                return
            current_index = self.notebook.index(selected_tab_path) # type: ignore[misc]
            if isinstance(current_index, int):
                 self.close_tab_at_index(current_index)
            else:
                logging.warning(f"Could not determine index for tab: {selected_tab_path}")
        except (tk.TclError, AttributeError) as e:
            logging.error("Error closing current tab: %s", e)

    def open_curve_fitting_tab(self):
        """Open a new curve fitting tab"""
        try:
            i = 1
            while f'curve_fitting_{i}' in self.open_tabs:
                i += 1
            tab_key = f'curve_fitting_{i}'

            tab_main_frame = ttk.Frame(self.notebook)
            self.notebook.add(
                tab_main_frame,
                text=TRANSLATIONS[self.language]['curve_fitting']
            )

            content_area = self.add_close_button_to_tab(tab_main_frame)
            
            # Create the AjusteCurvaFrame and pack it to fill the content area
            curve_fitting_instance = AjusteCurvaFrame(content_area, self.language)
            curve_fitting_instance.pack(fill=tk.BOTH, expand=True)
            
            self.open_tabs[tab_key] = {
                'widget': tab_main_frame,
                'instance': curve_fitting_instance
            }
            self.notebook.select(tab_main_frame) # type: ignore[misc]

        except Exception as e:
            import traceback
            error_msg = f"Failed to create tab: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg) # type: ignore[misc]

    def open_uncertainty_calc_tab(self):
        """Open uncertainty calculator tab"""
        try:
            i = 1
            while f'uncertainty_calc_{i}' in self.open_tabs:
                i += 1
            tab_key = f'uncertainty_calc_{i}'

            tab_main_frame = ttk.Frame(self.notebook)
            self.notebook.add(
                tab_main_frame,
                text=TRANSLATIONS[self.language]['uncertainty_calc']
            )
            
            content_area = self.add_close_button_to_tab(tab_main_frame)

            uncertainty_calc_instance = CalculoIncertezasFrame(content_area, self.language)

            self.open_tabs[tab_key] = {
                'widget': tab_main_frame,
                'instance': uncertainty_calc_instance
            }
            self.notebook.select(tab_main_frame) # type: ignore[misc]
            
            # No need to return tab_main_frame explicitly unless used by caller
            # return tab_main_frame 
        except (ImportError, AttributeError, tk.TclError) as e:
            messagebox.showerror("Error", f"Failed to create tab: {str(e)}")  # type: ignore[misc]
            return None

    def switch_language(self, new_language: str) -> None:
        """Switch the application language"""
        if new_language in ['pt', 'en'] and new_language != self.language:
            self.language = new_language
            # Update the dropdown to reflect the change
            if hasattr(self, 'lang_var') and self.lang_var is not None:
                self.lang_var.set("Português" if new_language == 'pt' else "English")
            self.update_ui_language()

    def on_tab_changed(self, event: Optional[Any] = None) -> None:
        """Handle tab changed event"""
        _ = event
        _tab_ids_tuple = self.notebook.tabs() # type: ignore[misc]
        if not _tab_ids_tuple: 
            return
        # tab_ids_raw = cast(Tuple[str, ...], _tab_ids_tuple) # Not strictly needed if only select() is used next
        try:
            current_tab_path = self.notebook.select() # type: ignore[misc]
            if not current_tab_path:
                return
            
            current_widget = self.notebook.nametowidget(current_tab_path) # type: ignore[misc]
            found_instance = None
            for tab_data_entry in self.open_tabs.values():
                if isinstance(tab_data_entry, dict): # Check if it's TabData
                    if tab_data_entry.get('widget') == current_widget:
                        found_instance = tab_data_entry.get('instance')
                        break
            
            if found_instance and hasattr(found_instance, 'on_tab_activated'):
                found_instance.on_tab_activated()
        except tk.TclError as e:
            print(f"Error in tab changed: {e}")

    def on_close(self) -> None:
        """Handle application close"""
        # Clean up resources
        for tab_data_entry in self.open_tabs.values():
            if isinstance(tab_data_entry, dict): # Check if it's TabData
                tab_instance = tab_data_entry.get('instance')
                if tab_instance and hasattr(tab_instance, 'cleanup'):
                    tab_instance.cleanup()

        self.root.quit()
        self.root.destroy()

    def run(self) -> None:
        """Start the application"""
        # Maximize window on startup
        self.root.state('zoomed')
        self.root.mainloop()

    def setup_home_tab(self):
        """Set up the home tab with welcome content"""
        # Create a welcome frame with a nice header
        welcome_frame = ttk.Frame(self.home_tab)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create a frame for the app name and version to display them side by side
        header_frame = ttk.Frame(welcome_frame)
        header_frame.pack(pady=(30, 10))

        # Add welcome message
        app_name_label = ttk.Label(
            header_frame,
            text="AnaFis",
            font=("Segoe UI", 24, "bold")
        )
        app_name_label.pack(side=tk.LEFT)

        # Add version with different styling
        version_label = ttk.Label(
            header_frame,
            text=f"v{__version__}",
            font=("Segoe UI", 12),
            foreground="#666666"  # Gray color for the version
        )
        version_label.pack(
            side=tk.LEFT,
            padx=(5, 0),
            pady=(10, 0)
        )  # Align with bottom of the app name

        # Add description
        description = ttk.Label(
            welcome_frame,
            text=TRANSLATIONS[self.language]['app_title'],
            font=("Segoe UI", 14)
        )
        description.pack(pady=(0, 30))

        # Add buttons for main functions with larger icons/text
        button_frame = ttk.Frame(welcome_frame)
        button_frame.pack(pady=20)

        # Curve fitting button
        curve_btn = ttk.Button(
            button_frame,
            text=TRANSLATIONS[self.language]['curve_fitting'],
            command=self.open_curve_fitting_tab,
            width=25
        )
        curve_btn.pack(pady=10)

        # Uncertainty calculator button
        uncertainty_btn = ttk.Button(
            button_frame,
            text=TRANSLATIONS[self.language]['uncertainty_calc'],
            command=self.open_uncertainty_calc_tab,
            width=25
        )
        uncertainty_btn.pack(pady=10)

        # Settings button
        settings_btn = ttk.Button(
            button_frame,
            text=TRANSLATIONS[self.language].get('settings', 'Configurações'),
            command=self.open_settings_dialog,
            width=25
        )
        settings_btn.pack(pady=10)

    def open_settings_dialog(self):
        """Open settings dialog to configure user preferences"""
        # Create and show settings dialog
        dialog = SettingsDialog(self.root, self.language, callback=self.on_settings_changed)
        self.root.wait_window(dialog.top)

    def on_settings_changed(self, updated_settings: Dict[str, Any]) -> None:
        """Handle when settings are changed

        Args:
            updated_settings: Dictionary of settings that were updated
        """
        # Check if language was changed
        if 'language' in updated_settings:
            self.language = updated_settings['language']
            self.update_ui_language()

        # Apply other settings as needed
