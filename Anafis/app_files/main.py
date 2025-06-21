"""Main application module"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging
import os
from typing import Any, Dict, List, Optional, Protocol, Tuple, TypedDict, Union, cast, Callable

# Import the version from app_files package
from app_files import __version__

from app_files.utils.constants import TRANSLATIONS
from app_files.utils.user_preferences import user_preferences
from app_files.utils.lazy_loader import lazy_import

# Lazy imports for heavy GUI components - these will only load when needed
AjusteCurvaFrame = lazy_import('app_files.gui.ajuste_curva.main_gui', 'AjusteCurvaFrame')
CalculoIncertezasFrame = lazy_import('app_files.gui.incerteza.calculo_incertezas_gui', 'CalculoIncertezasFrame')
SettingsDialog = lazy_import('app_files.gui.settings.settings_dialog', 'SettingsDialog')

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

    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        # Use provided root or create a new one
        self.root = root if root is not None else tk.Tk()

        # Load language from user preferences - explicitly type as str
        self.language: str = user_preferences.get_preference('language', 'pt')

        # Initialize UI component attributes with proper typing
        self.lang_label: Optional[ttk.Label] = None
        self.lang_var: Optional[tk.StringVar] = None
        self.lang_dropdown: Optional[ttk.Combobox] = None
        self.toolbar_frame: Optional[ttk.Frame] = None
        self.notebook: Optional[ttk.Notebook] = None  
        self.home_tab: Optional[ttk.Frame] = None
        self.tab_menu: Optional[tk.Menu] = None
        self.icon: Optional[tk.PhotoImage] = None        
        # Use the TabData TypedDict for open_tabs
        self.open_tabs: Dict[str, Union[TabData, str]] = {}

        # Only setup UI if this is a new window (not reusing splash)
        if root is None:
            self.setup_ui()

    def setup_ui(self):
        """Set up the main application UI"""
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
        
        self.root.geometry("1200x800")
        
        # Ensure the window is resizable
        self.root.resizable(True, True)
              
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_app_icon(self):
        """Set the application icon from utils/icon.png"""
        try:
            # Check if icon is already set (to avoid conflicts with splash screen)
            if hasattr(self.root, '_icon_set') and self.root._icon_set:  # type: ignore
                return
                
            # Get the path to the icon file in the utils folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            utils_dir = os.path.join(current_dir, 'utils')
            icon_path = os.path.join(utils_dir, 'icon.png')

            # Check if the icon file exists
            if not os.path.exists(icon_path):
                logging.warning("Icon file not found at: %s", icon_path)
                return

            # Create a PhotoImage from the icon file with a unique name
            icon = tk.PhotoImage(file=icon_path, name=f"main_app_icon_{id(self)}")

            # Set as application icon
            self.root.iconphoto(True, icon)

            # Store the icon to prevent garbage collection
            self.icon = icon
            
            # Mark as set to prevent future conflicts
            self.root._icon_set = True  # type: ignore

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
            value=TRANSLATIONS[self.language][f'language_{self.language}'])
        self.lang_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=[TRANSLATIONS[self.language]['language_pt'], TRANSLATIONS[self.language]['language_en']],
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
        # Map the language display name back to language code
        new_language = self._get_language_code_from_name(selected)

        if new_language != self.language:
            self.language = new_language
            # Save the language preference
            user_preferences.set_preference('language', new_language)
            self.update_ui_language()
            
    def _get_language_code_from_name(self, language_name: str) -> str:
        """Convert a language display name to its code."""
        if language_name == TRANSLATIONS[self.language]['language_pt']:
            return 'pt'
        elif language_name == TRANSLATIONS[self.language]['language_en']:
            return 'en'
        # Default to English if unknown
        return 'en'

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
                
        # Update language dropdown values
        if hasattr(self, 'lang_dropdown') and self.lang_dropdown is not None and hasattr(self, 'lang_var') and self.lang_var is not None:
            current_lang_name = TRANSLATIONS[self.language][f'language_{self.language}']
            self.lang_var.set(current_lang_name)
            self.lang_dropdown.configure(
                values=[TRANSLATIONS[self.language]['language_pt'], TRANSLATIONS[self.language]['language_en']]
            )

        # Update all open tabs
        self._update_open_tab_instances()
        # Update tab texts in notebook
        self._update_notebook_tabs()
        # Refresh home tab to update all text
        if hasattr(self, 'home_tab') and self.home_tab is not None:
            for widget in self.home_tab.winfo_children():
                widget.destroy()
            self.setup_home_tab()

    def _update_toolbar_buttons(self):
        """Update toolbar button texts to current language"""
        if self.toolbar_frame is not None:
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
                        TRANSLATIONS['en']['uncertainty_calc']
                    ]:
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
            if self.tab_menu is not None:
                self.tab_menu.post(event.x_root, event.y_root)
        except tk.TclError as e:
            logging.debug(f"Tab right-click TclError: {e}")

    def close_current_tab(self):
        """Close the currently selected tab"""
        if self.notebook is None:
            return
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

    def _show_loading_indicator(self, parent: tk.Widget, message: str) -> tk.Label:
        """Show a loading indicator while heavy components are being imported"""
        loading_label = tk.Label(
            parent, 
            text=f"🔄 {message}...",
            font=("Arial", 12),
            fg="gray"
        )
        loading_label.pack(expand=True)
        parent.update()  # Force immediate display
        return loading_label
    
    def _hide_loading_indicator(self, loading_widget: tk.Widget) -> None:
        """Hide the loading indicator"""
        try:
            loading_widget.destroy()
        except tk.TclError:
            pass  # Widget already destroyed

    def open_curve_fitting_tab(self):
        """Open a new curve fitting tab"""
        try:
            i = 1
            while f'curve_fitting_{i}' in self.open_tabs:
                i += 1
            tab_key = f'curve_fitting_{i}'

            tab_main_frame = ttk.Frame(self.notebook)
            if self.notebook is not None:
                self.notebook.add(
                    tab_main_frame,
                    text=TRANSLATIONS[self.language]['curve_fitting']
                )

            content_area = self.add_close_button_to_tab(tab_main_frame)
            
            # Ensure notebook exists before creating tab content
            if self.notebook is None:
                logging.error("Notebook is not initialized")
                return
            
            # Show loading indicator while heavy components are being imported
            loading_indicator = self._show_loading_indicator(
                content_area, 
                TRANSLATIONS[self.language].get('loading_curve_fitting', 'Loading curve fitting module')
            )
            
            try:
                # Create the AjusteCurvaFrame and pack it to fill the content area
                curve_fitting_instance = AjusteCurvaFrame(content_area, self.language)
                
                # Hide loading indicator
                self._hide_loading_indicator(loading_indicator)
                
                curve_fitting_instance.pack(fill=tk.BOTH, expand=True)
                
                self.open_tabs[tab_key] = {
                    'widget': tab_main_frame,
                    'instance': curve_fitting_instance
                }
                
                # Safely select the tab
                try:
                    self.notebook.select(tab_main_frame) # type: ignore[misc]
                except Exception as select_error:
                    logging.warning(f"Could not select tab: {select_error}")
                    
            except Exception as load_error:
                # Hide loading indicator in case of error
                self._hide_loading_indicator(loading_indicator)
                logging.error(f"Failed to create curve fitting tab: {load_error}")
                messagebox.showerror(  # type: ignore[reportUnknownMemberType]
                    TRANSLATIONS[self.language]['error'],
                    TRANSLATIONS[self.language].get('curve_fitting_load_error', 
                                                   f'Failed to load curve fitting module: {load_error}')
                )
                return

        except Exception as e:
            import traceback
            error_msg = f"Failed to create tab: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            messagebox.showerror(TRANSLATIONS[self.language]['error'], # type: ignore[misc]
                               TRANSLATIONS[self.language]['tab_creation_error_detailed'].format(error=str(e))) # type: ignore[misc]

    def open_uncertainty_calc_tab(self):
        """Open uncertainty calculator tab"""
        try:
            i = 1
            while f'uncertainty_calc_{i}' in self.open_tabs:
                i += 1
            tab_key = f'uncertainty_calc_{i}'

            tab_main_frame = ttk.Frame(self.notebook)
            if self.notebook is not None:
                self.notebook.add(
                    tab_main_frame,
                    text=TRANSLATIONS[self.language]['uncertainty_calc']
                )
            
            content_area = self.add_close_button_to_tab(tab_main_frame)

            # Show loading indicator while heavy components are being imported
            loading_indicator = self._show_loading_indicator(
                content_area, 
                TRANSLATIONS[self.language].get('loading_uncertainty_calc', 'Loading uncertainty calculator')
            )
            
            try:
                uncertainty_calc_instance = CalculoIncertezasFrame(content_area, self.language)
                
                # Hide loading indicator
                self._hide_loading_indicator(loading_indicator)

                self.open_tabs[tab_key] = {
                    'widget': tab_main_frame,
                    'instance': uncertainty_calc_instance
                }
                self.notebook.select(tab_main_frame) # type: ignore[misc]
                
            except Exception as load_error:
                # Hide loading indicator in case of error
                self._hide_loading_indicator(loading_indicator)
                logging.error(f"Failed to create uncertainty calculator tab: {load_error}")
                messagebox.showerror(  # type: ignore[reportUnknownMemberType]
                    TRANSLATIONS[self.language]['error'],
                    TRANSLATIONS[self.language].get('uncertainty_calc_load_error', 
                                                   f'Failed to load uncertainty calculator: {load_error}')
                )
                return None
            
            # No need to return tab_main_frame explicitly unless used by caller
            # return tab_main_frame 
        except (ImportError, AttributeError, tk.TclError) as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], # type: ignore[misc]
                               TRANSLATIONS[self.language]['tab_creation_error_detailed'].format(error=str(e)))  # type: ignore[misc]
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
            logging.error(f"Error in tab changed: {e}")

    def on_close(self) -> None:
        """Handle application close"""
        try:
            # Clean up resources
            for tab_data_entry in self.open_tabs.values():
                if isinstance(tab_data_entry, dict): # Check if it's TabData
                    tab_instance = tab_data_entry.get('instance')
                    if tab_instance and hasattr(tab_instance, 'cleanup'):
                        try:
                            tab_instance.cleanup()
                        except Exception as e:
                            logging.debug(f"Error during tab cleanup: {e}")

            # Clean up matplotlib figures to prevent memory leaks
            try:
                import matplotlib.pyplot as plt
                plt.close('all')
            except Exception as e:
                logging.debug(f"Error closing matplotlib figures: {e}")

            # Stop the main loop and destroy the window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logging.error(f"Error during application close: {e}")
        finally:
            # Force exit the process to ensure it terminates
            import os
            try:
                # Give a brief moment for cleanup to complete
                import time
                time.sleep(0.1)
            except:
                pass
            # Force terminate the process
            os._exit(0)

    def run(self) -> None:
        """Start the application"""
        # Maximize window immediately for fastest startup
        try:
            # First ensure window is in normal state
            self.root.wm_state('normal')
            self.root.update_idletasks()
            self._immediate_maximize()
        except Exception as e:
            logging.warning(f"Could not maximize window immediately: {e}")
        
        self.root.mainloop()
    
    def _maximize_with_geometry(self, reason: str) -> None:
        """Fallback maximization using geometry calculation"""
        logging.info(f"Using geometry maximization: {reason}")
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Platform-specific taskbar/dock space calculations
        import platform
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
        logging.info(f"Setting geometry: {geometry_string}")
        self.root.geometry(geometry_string)

    def _immediate_maximize(self) -> None:
        """Immediately maximize the window without centering (fallback method)"""
        import platform
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows: use 'zoomed' state (equivalent to clicking maximize button)
                self.root.after(100, lambda: self.root.wm_state('zoomed'))
                logging.info("Window set to maximized state (Windows zoomed)")
                
            elif system == "Darwin":  # macOS
                # macOS: try zoomed state first, then attributes
                try:
                    self.root.wm_state('zoomed')
                    logging.info("Window maximized using zoomed state (macOS)")
                except tk.TclError:
                    # macOS fallback: use attributes
                    self.root.wm_attributes('-fullscreen', False)  # type: ignore[misc]
                    self.root.wm_attributes('-zoomed', True)  # type: ignore[misc]
                    logging.info("Window maximized using attributes (macOS)")
                    
            elif system == "Linux":
                # Linux: try different methods depending on window manager
                try:
                    # Method 1: Try zoomed attribute (works with some WMs)
                    self.root.wm_attributes('-zoomed', True)  # type: ignore[misc]
                    logging.info("Window maximized using -zoomed attribute (Linux)")
                except tk.TclError:
                    try:
                        # Method 2: Try zoomed state (works with some WMs)
                        self.root.wm_state('zoomed')
                        logging.info("Window maximized using zoomed state (Linux)")
                    except tk.TclError:
                        # Method 3: Use geometry for Linux (most compatible)
                        self._maximize_with_geometry("Linux fallback")
            else:
                # Unknown platform: try zoomed state first
                try:
                    self.root.wm_state('zoomed')
                    logging.info(f"Window maximized using zoomed state ({system})")
                except tk.TclError:
                    self._maximize_with_geometry(f"{system} fallback")
                    
        except Exception as e:
            logging.warning(f"Could not maximize window: {e}")
            self._maximize_with_geometry("Exception fallback")

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
        from app_files.utils.theme_manager import theme_manager
        version_label = ttk.Label(
            header_frame,
            text=f"v{__version__}",
            font=("Segoe UI", 12),
            foreground=theme_manager.get_adaptive_color('text_info')
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

    def initialize_utilities(self, progress_callback: Optional[Callable[[int, str], None]] = None):
        """Initialize the utility modules for the application"""
        
        if progress_callback:
            progress_callback(93, "Checking for updates...")
        
        # Import and initialize update checker 
        from app_files.utils.update_checker import update_checker
        update_checker.initialize()
        
        if progress_callback:
            progress_callback(95, "Loading theme system...")
        
        # Import and initialize theme manager
        from app_files.utils.theme_manager import theme_manager
        if not theme_manager.is_initialized:
            theme_manager.initialize(self.root)
        
        if progress_callback:
            progress_callback(97, "Applying theme...")
        
        # Apply current theme from preferences (this triggers TTK theme loading)
        theme = user_preferences.get_preference('theme', 'vista')
        theme_manager.apply_theme(theme)
        
        if progress_callback:
            progress_callback(100, "Application ready!")
