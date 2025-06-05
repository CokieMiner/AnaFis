"""Main application module"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging

# Import the version from app_files package
from app_files import __version__  # Add this import

from app_files.utils.constants import TRANSLATIONS
from app_files.utils.user_preferences import user_preferences
from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
from app_files.gui.incerteza.calculo_incertezas_gui import CalculoIncertezasFrame


class AplicativoUnificado:
    """Main application class with tabbed interface"""
    def __init__(self) -> None:
        self.root = tk.Tk()
        # Load language from user preferences
        self.language = user_preferences.get_preference('language', 'pt')
        
        # Create tab context menu
        self.tab_menu = tk.Menu(self.root, tearoff=0)
        self.tab_menu.add_command(
            label="Close", 
            command=self.close_current_tab
        )
        
        # Add dictionary to track open tabs
        self.open_tabs = {}
        
        # Set title
        self.root.title(TRANSLATIONS[self.language]['app_title'])
        
        # Setup main UI components
        self.setup_toolbar()
        self.setup_notebook()
        
        # Configure root layout
        self.root.geometry("1200x800")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)    
        
    def setup_toolbar(self):
        """Set up toolbar with application controls"""
        # Create toolbar frame
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        # Configure toolbar columns
        self.toolbar_frame.columnconfigure(0, weight=0)  # Curve fitting button
        self.toolbar_frame.columnconfigure(1, weight=0)  # Uncertainty button
        self.toolbar_frame.columnconfigure(2, weight=1)  # Empty space
        self.toolbar_frame.columnconfigure(3, weight=0)  # Language label
        
        # Add buttons to toolbar
        curve_fit_btn = ttk.Button(self.toolbar_frame, 
                  text=TRANSLATIONS[self.language]['curve_fitting'],
                  command=self.open_curve_fitting_tab)
        curve_fit_btn.grid(row=0, column=0, padx=5, sticky="w")
        
        uncertainty_btn = ttk.Button(self.toolbar_frame, 
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
        self.lang_label = ttk.Label(lang_frame, text=TRANSLATIONS[self.language]['language_label'])
        self.lang_label.grid(row=0, column=0, padx=(0, 5))
        
        # Language dropdown
        self.lang_var = tk.StringVar(value="Português" if self.language == 'pt' else "English")
        self.lang_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["Português", "English"],
            state="readonly",
            width=10
        )
        self.lang_dropdown.grid(row=0, column=1)
        self.lang_dropdown.bind('<<ComboboxSelected>>', self.on_language_changed)
        
    def on_language_changed(self, event=None):
        """Handle language dropdown selection change"""
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
        for widget in self.toolbar_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                if widget.cget('text') in [TRANSLATIONS['pt']['curve_fitting'], TRANSLATIONS['en']['curve_fitting']]:
                    widget.configure(text=TRANSLATIONS[self.language]['curve_fitting'])
                elif widget.cget('text') in [TRANSLATIONS['pt']['uncertainty_calc'], TRANSLATIONS['en']['uncertainty_calc']]:
                    widget.configure(text=TRANSLATIONS[self.language]['uncertainty_calc'])
    
        # Update language label
        if hasattr(self, 'lang_label'):
            self.lang_label.configure(text=TRANSLATIONS[self.language]['language_label'])
    
        # Update all open tabs
        for tab_instance in self.open_tabs.values():
            if hasattr(tab_instance, 'switch_language'):
                tab_instance.switch_language(self.language)
    
        # Update tab texts in notebook
        for i, tab_id in enumerate(self.notebook.tabs()):
            tab_text = self.notebook.tab(i, 'text')
            if tab_text in [TRANSLATIONS['pt']['curve_fitting'], TRANSLATIONS['en']['curve_fitting']]:
                self.notebook.tab(i, text=TRANSLATIONS[self.language]['curve_fitting'])
            elif tab_text in [TRANSLATIONS['pt']['uncertainty_calc'], TRANSLATIONS['en']['uncertainty_calc']]:
                self.notebook.tab(i, text=TRANSLATIONS[self.language]['uncertainty_calc'])
            elif tab_text in [TRANSLATIONS['pt']['home'], TRANSLATIONS['en']['home']]:
                self.notebook.tab(i, text=TRANSLATIONS[self.language]['home'])
            
        # Refresh home tab to update all text
        if hasattr(self, 'home_tab'):
            for widget in self.home_tab.winfo_children():
                widget.destroy()
            self.setup_home_tab()

    def restore_tab_close_buttons(self):
        """Check all tabs and restore close buttons if missing"""
        for tab_id in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab_id)
            if not hasattr(tab_frame, 'close_button') or not tab_frame.close_button.winfo_exists():
                self.add_close_button_to_tab(tab_frame)
                
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
        self.setup_home_tab()
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Bind right-click event for context menu
        self.notebook.bind("<Button-3>", self.on_tab_right_click)
    
    def monitor_tabs(self):
        """Periodically check tabs to ensure close buttons are visible"""
        # Skip the home tab (first tab) which shouldn't have a close button
        for i, tab_id in enumerate(self.notebook.tabs()):
            if i > 0:  # Skip home tab
                tab_frame = self.notebook.nametowidget(tab_id)
                if not hasattr(tab_frame, 'close_button') or not tab_frame.close_button.winfo_exists():
                    self.add_close_button_to_tab(tab_frame)
    
        # Continue monitoring
        self.root.after(1000, self.monitor_tabs)
        
    def add_close_button_to_tab(self, tab_frame):
        """Add a close button to tab that stays in place even with resizing content"""
        # Skip adding close button if this is the home tab
        if tab_frame == self.home_tab:
            return
        
        # Create a container frame for the tab with fixed positioning for the button
        if not hasattr(tab_frame, 'header_frame'):
            # Create a header frame that will stay at the top of the tab
            header_frame = ttk.Frame(tab_frame)
            header_frame.pack(side=tk.TOP, fill=tk.X, anchor=tk.NE)
            
            # Create close button in the header frame
            close_button = ttk.Button(
                header_frame, 
                text="×", 
                width=2, 
                command=lambda t=tab_frame: self.try_close_tab(t)
            )
            close_button.pack(side=tk.RIGHT, anchor=tk.NE, padx=5, pady=5)
            
            # Use setattr to avoid Pylance warnings
            setattr(tab_frame, 'header_frame', header_frame)
            setattr(tab_frame, 'close_button', close_button)
            
            # If tab already has content, repack it below the header
            for widget in tab_frame.winfo_children():
                if widget != header_frame:
                    widget.pack_forget()
                    widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def try_close_tab(self, tab_frame):
        """Try to close a tab by finding its numeric index
        
        Args:
            tab_frame: The frame of the tab to close
        """
        try:
            # Find the tab's index
            for i, tab_id in enumerate(self.notebook.tabs()):
                if str(self.notebook.nametowidget(tab_id)) == str(tab_frame):
                    # Found the tab - close it
                    self.close_tab_at_index(i)
                    return
        except Exception as e:
            logging.error(f"Error finding tab to close: {e}")

    def close_tab_at_index(self, index):
        """Close a tab at a specific index
        
        Args:
            index: The index of the tab to close
        """
        try:
            # Prevent closing the home tab (index 0)
            if index == 0:
                return
                
            # Find the corresponding tab instance
            tab_to_close = None
            tab_name_to_close = None
            
            # Try to find by matching the index in the key name
            for tab_name, tab_instance in self.open_tabs.items():
                # Check if it's a curve fitting tab with matching index
                if 'curve_fitting' in tab_name and int(tab_name.split('_')[-1]) == index + 1:
                    tab_to_close = tab_instance
                    tab_name_to_close = tab_name
                    break
                # Check if it's an uncertainty tab with matching index
                elif 'uncertainty_calc' in tab_name and int(tab_name.split('_')[-1]) == index + 1:
                    tab_to_close = tab_instance
                    tab_name_to_close = tab_name
                    break
              # Clean up resources if needed
            if tab_to_close and hasattr(tab_to_close, 'cleanup'):
                try:
                    tab_to_close.cleanup()
                except Exception as e:
                    logging.error(f"Error in tab cleanup: {e}")
            
            # Remove from the dictionary if found
            if tab_name_to_close in self.open_tabs:
                del self.open_tabs[tab_name_to_close]
            
            # Remove the tab from the notebook
            self.notebook.forget(index)
        except Exception as e:
            logging.error(f"Error closing tab: {e}")
    
    def on_tab_right_click(self, event):
        """Show context menu on right-click"""
        try:
            # First check if there are any tabs
            if not self.notebook.tabs():
                return  # No tabs to show menu for
              # Try to identify which tab was clicked
            try:
                tab_index = self.notebook.index("@%d,%d" % (event.x, event.y))
                
                # If we got a valid index, select that tab
                if tab_index >= 0:
                    self.notebook.select(tab_index)
                    
                    # Don't show close option for home tab (index 0)
                    if tab_index == 0:
                        return
            except Exception:
                # If there was an error identifying the tab, just continue
                pass
            
            # Display the context menu at cursor position
            self.tab_menu.post(event.x_root, event.y_root)
        except Exception as e:
            # Ignore clicks that don't hit a tab
            logging.error(f"Tab right-click error: {e}")

    def close_current_tab(self):
        """Close the currently selected tab"""
        try:
            # Get the current tab index
            current_index = self.notebook.index(self.notebook.select())
            
            # Close the tab at that index
            self.close_tab_at_index(current_index)
        except Exception as e:
            logging.error(f"Error closing current tab: {e}")

    def open_curve_fitting_tab(self):
        """Open a new curve fitting tab"""
        try:
            # Find the next available index for curve fitting tabs
            i = 1
            while f'curve_fitting_{i}' in self.open_tabs:
                i += 1
            
            # Create a new tab with a special container structure
            tab_frame = ttk.Frame(self.notebook)
            
            # Create a header frame with fixed position at the top
            header_frame = ttk.Frame(tab_frame)
            header_frame.pack(side=tk.TOP, fill=tk.X)
            
            # Add a close button that will stay in place
            close_button = ttk.Button(
                header_frame, 
                text="×", 
                width=2,
                command=lambda: self.try_close_tab(tab_frame)
            )
            close_button.pack(side=tk.RIGHT, padx=5, pady=5)
            
            # Create a content frame for the tab content
            content_frame = ttk.Frame(tab_frame)
            content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Initialize the curve fitting module in the content frame
            curve_fitting = AjusteCurvaFrame(content_frame, self.language)
            
            # Add the tab to the notebook
            self.notebook.add(tab_frame, text=TRANSLATIONS[self.language]['curve_fitting'])
            self.notebook.select(tab_frame)
            
            # Store references
            setattr(tab_frame, 'close_button', close_button)
            setattr(tab_frame, 'header_frame', header_frame)
            setattr(tab_frame, 'content_frame', content_frame)
            self.open_tabs[f'curve_fitting_{i}'] = curve_fitting
        except Exception as e:
            logging.error(f"Error opening curve fitting tab: {e}")

    def open_uncertainty_calc_tab(self):
        """Open uncertainty calculator tab"""
        try:
            # Create a new tab frame
            tab = ttk.Frame(self.notebook)
            
            # Add the tab to the notebook
            self.notebook.add(tab, text=TRANSLATIONS[self.language]['uncertainty_calc'])
            
            # Add a close button to the tab
            self.add_close_button_to_tab(tab)
            
            # Create tab instance  
            uncertainty_calc = CalculoIncertezasFrame(tab, self.language)
            
            # Generate unique key similar to curve fitting tabs
            tab_key = f"uncertainty_calc_{len([k for k in self.open_tabs.keys() if 'uncertainty_calc' in k]) + 1}"
            
            # Store reference to the tab instance
            self.open_tabs[tab_key] = uncertainty_calc
            
            # Select the newly created tab (it's the last one)
            self.notebook.select(len(self.notebook.tabs()) - 1)
            
            return tab
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create tab: {str(e)}")
            return None
    def switch_language(self, new_language):
        """Switch the application language"""
        if new_language in ['pt', 'en'] and new_language != self.language:
            self.language = new_language
            # Update the dropdown to reflect the change
            if hasattr(self, 'lang_var'):
                self.lang_var.set("Português" if new_language == 'pt' else "English")
            self.update_ui_language()
                
    def on_tab_changed(self, event):
        """Handle tab changed event"""
        # Only activate if there are tabs
        if not self.notebook.tabs():
            return
            
        # Get the current tab index
        try:
            current_tab = self.notebook.select()
            if not current_tab:
                return
                
            current_index = self.notebook.index(current_tab)
                
            # Activate all tabs - simpler and more reliable
            for tab_instance in self.open_tabs.values():
                if hasattr(tab_instance, 'on_tab_activated'):
                    tab_instance.on_tab_activated()
                    
        except Exception as e:
            print(f"Error in tab changed: {e}")

    def on_close(self) -> None:
        """Handle application close"""
        # Clean up resources
        for tab_instance in self.open_tabs.values():
            if hasattr(tab_instance, 'cleanup'):
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
        # Import the version constant
        from app_files import __version__
        
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
        version_label.pack(side=tk.LEFT, padx=(5, 0), pady=(10, 0))  # Align with bottom of the app name
        
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
            text=TRANSLATIONS[self.language]['settings'],
            command=self.open_settings_dialog,
            width=25
        )
        settings_btn.pack(pady=10)
        
    def open_settings_dialog(self):
        """Open settings dialog to configure user preferences"""
        from app_files.gui.settings.settings_dialog import SettingsDialog
    
        # Create and show settings dialog
        dialog = SettingsDialog(self.root, self.language, callback=self.on_settings_changed)
        self.root.wait_window(dialog.top)
    
    def on_settings_changed(self, updated_settings):
        """Handle when settings are changed
    
        Args:
            updated_settings: Dictionary of settings that were updated
        """
        # Check if language was changed
        if 'language' in updated_settings:
            self.language = updated_settings['language']
            self.update_ui_language()
        
        # Apply other settings as needed
