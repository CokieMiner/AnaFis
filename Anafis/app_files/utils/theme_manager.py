"""
Theme manager for AnaFis application.
Manages application themes including built-in TTK themes and custom TCL themes.
"""
import logging
import os
import tkinter as tk
from tkinter import ttk
from typing import List, Set, Any, Optional, Dict, Callable

class ThemeManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args: Any, **kwargs: Any):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized: # Proper singleton init check
            return
        
        logging.info("Creating ThemeManager singleton instance (uninitialized).")
        self.themes_directory: str = self.get_themes_directory()
        self.available_themes: List[str] = []
        self.loaded_custom_themes: Set[str] = set()
        self.root: Optional[tk.Tk] = None
        self._initialized = False
        self._color_callbacks: List[Callable[[], None]] = []
        
        # Performance optimizations
        self._theme_colors_cache: Dict[str, Dict[str, str]] = {}
        self._needs_full_update = False

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
        logging.info(f"ThemeManager initialized. {len(self.available_themes)} themes available.")

    def get_themes_directory(self) -> str:
        """Gets the path to the user's custom themes directory."""
        if os.name == 'nt':
            appdata = os.environ.get('APPDATA')
            if appdata:
                return os.path.join(appdata, 'AnaFis', 'themes')
            else:
                # Fallback for unusual cases where APPDATA is not set
                return os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'AnaFis', 'themes')
        else:
            # For Unix-like systems
            return os.path.expanduser('~/.config/anafis/themes')

    def _load_all_themes(self):
        """Load all available themes: built-in, well-known packages, and those from theme_packages.txt"""
        if not self.root:
            logging.error("ThemeManager not initialized. Cannot load themes.")
            return
            
        logging.info("Loading all available themes...")
        
        try:
            # Force ttk initialization by creating and destroying a widget
            dummy_widget = ttk.Frame(self.root)
            dummy_widget.destroy()

            style = ttk.Style(self.root)
            builtin_themes: Set[str] = set(style.theme_names())
        except tk.TclError as e:
            logging.error(f"Could not retrieve built-in TTK themes: {e}")
            builtin_themes = set()
        
        if builtin_themes:
            logging.info(f"Successfully retrieved {len(builtin_themes)} built-in themes: {sorted(list(builtin_themes))}")
        else:
            logging.warning("No built-in themes were found. This might indicate a problem with the Tcl/Tk installation.")

        self.available_themes = sorted(list(builtin_themes))
        
        # Load well-known theme packages
        self._load_known_theme_packages()
          # Load themes from theme_packages.txt file
        self._load_themes_from_file()

    def _load_known_theme_packages(self) -> None:
        """Load well-known theme packages that might be installed"""
        known_packages: Dict[str, List[str]] = {
            'ttkthemes': [],  # Will get actual theme names from the package
            'ttkbootstrap': ['cosmo', 'flatly', 'journal', 'literal', 'lumen', 'minty', 'pulse', 'sandstone', 'united', 'yeti', 'morph', 'simplex', 'cerculean']
        }
        
        for package_name, theme_names in known_packages.items():
            try:
                if package_name == 'ttkthemes':
                    # Try to import ttkthemes and get available themes
                    import ttkthemes  # type: ignore
                    from ttkthemes import ThemedStyle  # type: ignore
                    themed_style = ThemedStyle(self.root)
                    available: List[str] = themed_style.theme_names()
                    # Filter out themes that are already in built-in themes
                    new_themes: List[str] = [t for t in available if t not in self.available_themes]
                    self.available_themes.extend(new_themes)
                    logging.info(f"Loaded {len(new_themes)} themes from ttkthemes: {new_themes}")
                elif package_name == 'ttkbootstrap':
                    # ttkbootstrap themes require special handling and are not standard TTK themes
                    # For now, we'll skip them as they need a different application method
                    logging.info(f"ttkbootstrap package detected but themes require special handling - skipping for now")
                else:
                    # For other packages, just try to import and add the known themes
                    __import__(package_name.replace('-', '_'))
                    new_themes = [t for t in theme_names if t not in self.available_themes]
                    self.available_themes.extend(new_themes)
                    logging.info(f"Loaded themes from {package_name}: {new_themes}")
                    
            except ImportError:
                logging.debug(f"Package {package_name} not available")
            except Exception as e:
                logging.warning(f"Error loading themes from {package_name}: {e}")

    def _load_themes_from_file(self) -> None:
        """Load theme packages specified in theme_packages.txt"""
        theme_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'theme_packages.txt')
        
        if not os.path.exists(theme_file):
            logging.debug(f"Theme packages file not found: {theme_file}")
            return
            
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        # Try to import the package
                        package_name = line.replace('-', '_')
                        __import__(package_name)
                          # If successful, try to get theme names
                        if 'ttkthemes' in line:
                            import ttkthemes  # type: ignore
                            from ttkthemes import ThemedStyle  # type: ignore
                            themed_style = ThemedStyle(self.root)
                            available = themed_style.theme_names()
                            new_themes = [t for t in available if t not in self.available_themes]
                            self.available_themes.extend(new_themes)
                            logging.info(f"Loaded themes from {line}: {new_themes}")
                        elif 'ttkbootstrap' in line:
                            import ttkbootstrap  # type: ignore
                            # ttkbootstrap themes require special handling - skip for now
                            logging.info(f"ttkbootstrap package detected in theme_packages.txt but themes require special handling - skipping")
                        else:
                            # For other packages, add some common theme names
                            potential_themes = [line, f"{line}-light", f"{line}-dark"]
                            new_themes = [t for t in potential_themes if t not in self.available_themes]
                            self.available_themes.extend(new_themes)
                            logging.info(f"Added potential themes from {line}: {new_themes}")
                            
                    except ImportError:
                        logging.debug(f"Package {line} from theme_packages.txt not available")
                    except Exception as e:
                        logging.warning(f"Error loading package {line}: {e}")
                        
        except Exception as e:
            logging.error(f"Error reading theme_packages.txt: {e}")

    def _load_custom_tcl_themes(self):
        """Legacy method - now disabled to improve performance"""
        logging.info("Custom TCL theme loading disabled for performance. Use theme packages instead.")

    def get_available_themes(self) -> List[str]:
        """Returns a sorted list of available theme names."""
        return sorted(list(set(self.available_themes)))

    def get_current_theme(self) -> str:
        """Gets the current theme from user preferences."""
        from app_files.utils.user_preferences import user_preferences
        return user_preferences.get_preference('theme', 'vista')

    def apply_theme(self, theme_name: str, save_preference: bool = True):
        """Applies the specified theme and optionally saves it to preferences."""
        if not self._initialized:
            logging.error("Cannot apply theme: ThemeManager not initialized.")
            return

        if theme_name == "default":
            theme_name = "vista" # Or another sensible default

        if theme_name not in self.get_available_themes():
            logging.error(f"Theme '{theme_name}' is not available. Cannot apply. Available: {self.get_available_themes()}")
            # Attempt to apply a fallback theme
            if "vista" in self.get_available_themes():
                self.apply_theme("vista", save_preference=save_preference)
            elif self.available_themes:
                self.apply_theme(self.available_themes[0], save_preference=save_preference)
            return

        try:
            ttk.Style().theme_use(theme_name)
            
            # Clear theme colors cache since we changed themes
            self._theme_colors_cache.clear()
            
            # Notify components to update their colors
            self._update_theme_dependent_colors()
            self._notify_color_callbacks()
            
            if save_preference:
                from app_files.utils.user_preferences import user_preferences
                user_preferences.set_preference('theme', theme_name)
                logging.info(f"Successfully applied and saved theme '{theme_name}'.")
            else:
                logging.info(f"Successfully applied theme '{theme_name}' (preview).")
        except tk.TclError as e:
            logging.error(f"Failed to apply theme '{theme_name}': {e}")
    
    def _update_theme_dependent_colors(self):
        """Update theme-dependent colors in UI components."""
        # This method can be extended to update specific UI components
        # For now, we'll rely on components checking colors when they need them        pass
    
    def register_color_update_callback(self, callback: Callable[[], None]):
        """Register a callback to be called when theme colors change."""
        if not hasattr(self, '_color_callbacks'):
            self._color_callbacks = []
        self._color_callbacks.append(callback)
        
    def _notify_color_callbacks(self):
        """Notify all registered callbacks about color changes."""
        if hasattr(self, '_color_callbacks'):
            for callback in self._color_callbacks:
                try:
                    callback()
                except Exception as e:
                    logging.warning(f"Color update callback failed: {e}")
          # Auto-update all Toplevel windows and Text widgets
        self._auto_update_widgets()
    
    def _auto_update_widgets(self):
        """Automatically update widgets with new theme colors - optimized version"""
        if not self._initialized or not self.root:
            return
            
        try:
            # Get current theme colors
            bg_color = self.get_adaptive_color('background')
            fg_color = self.get_adaptive_color('foreground')
            
            # Update root window background
            try:
                self.root.configure(bg=bg_color)
                logging.debug(f"Updated root window background to: {bg_color}")
            except tk.TclError:
                logging.warning("Could not update root window background")
              # Update TTK widgets efficiently using styles (most important)
            self._update_ttk_widgets(bg_color, fg_color)
            
            # Always update text widgets since they are important for readability
            self._update_text_widgets(self.root, bg_color, fg_color)
            
            # Call update_theme methods on widgets that have them
            self._call_update_theme_methods(self.root)
            
            # Only update specific widgets that need manual color changes
            # Skip the expensive recursive traversal unless necessary
            if hasattr(self, '_needs_full_update') and self._needs_full_update:
                # Find and update all Toplevel windows
                self._update_toplevel_windows(self.root, bg_color)
                # Find and update all Text widgets
                self._update_text_widgets(self.root, bg_color, fg_color)
                # Update other widgets that might have hardcoded colors
                self._update_other_widgets(self.root, bg_color, fg_color)
                # Reset the flag
                self._needs_full_update = False
                logging.debug("Performed full widget update")
            else:
                # Quick update - only update critical widgets
                self._quick_update_critical_widgets(bg_color, fg_color)
            
            logging.debug(f"Auto-updated widgets with theme colors: bg={bg_color}, fg={fg_color}")
            
        except Exception as e:
            logging.warning(f"Failed to auto-update widgets: {e}")
    
    def _quick_update_critical_widgets(self, bg_color: str, fg_color: str):
        """Quick update of only the most critical widgets for performance"""
        try:            # Only update widgets that are commonly visible and don't update automatically
            # This is a much faster alternative to full tree traversal
            
            # Update any visible dialogs or top-level windows
            if self.root:  # Add null check before accessing winfo_children
                for child in self.root.winfo_children():
                    if isinstance(child, tk.Toplevel):
                        try:
                            child.configure(bg=bg_color)
                        except tk.TclError:
                            pass
            
            logging.debug("Performed quick widget update")
            
        except Exception as e:
            logging.debug(f"Error in quick widget update: {e}")
    
    def request_full_update(self):
        """Request a full widget update on the next theme change"""        
        self._needs_full_update = True
    
    def _update_toplevel_windows(self, parent_widget: tk.Misc, bg_color: str):
        """Recursively find and update all Toplevel windows"""
        try:
            # Update Toplevel windows
            for child in parent_widget.winfo_children():
                if isinstance(child, tk.Toplevel):
                    try:
                        # Check if the window still exists before updating
                        if child.winfo_exists():
                            child.configure(bg=bg_color)
                            logging.debug(f"Updated Toplevel window background: {child.title()}")
                        else:
                            logging.debug(f"Skipped destroyed Toplevel window")
                    except (tk.TclError, AttributeError):
                        # Window might be destroyed or invalid
                        logging.debug(f"Skipped invalid Toplevel window: {type(child)}")
                        pass
                # Recursively check children
                try:
                    # Only recurse if the child widget still exists
                    if hasattr(child, 'winfo_exists') and child.winfo_exists():
                        self._update_toplevel_windows(child, bg_color)
                except (tk.TclError, AttributeError):
                    # Widget might be destroyed
                    logging.debug(f"Skipped destroyed widget during recursion: {type(child)}")
                    pass
                    
        except Exception as e:
            logging.debug(f"Error updating Toplevel windows: {e}")
    
    def _update_text_widgets(self, parent_widget: tk.Misc, bg_color: str, fg_color: str):
        """Recursively find and update all Text widgets"""
        try:
            # Check if current widget is a Text widget or ScrolledText
            if isinstance(parent_widget, tk.Text):
                try:
                    parent_widget.configure(bg=bg_color, fg=fg_color)
                    logging.debug(f"Updated Text widget colors")
                except tk.TclError:
                    # Widget might be destroyed or read-only
                    pass
            
            # Also check for ScrolledText specifically (though it inherits from Text)
            from tkinter.scrolledtext import ScrolledText
            if isinstance(parent_widget, ScrolledText):
                try:
                    parent_widget.configure(bg=bg_color, fg=fg_color)
                    logging.debug(f"Updated ScrolledText widget colors")
                except tk.TclError:
                    # Widget might be destroyed or read-only
                    pass
            
            # Recursively check children
            for child in parent_widget.winfo_children():
                try:
                    self._update_text_widgets(child, bg_color, fg_color)
                except tk.TclError:
                    # Widget might be destroyed
                    pass
                    
        except Exception as e:
            logging.debug(f"Error updating Text widgets: {e}")
    
    def _call_update_theme_methods(self, parent_widget: tk.Misc):
        """Recursively find and call update_theme methods on widgets that have them"""
        try:
            # Check if the parent widget still exists
            if not hasattr(parent_widget, 'winfo_exists'):
                return
                
            try:
                if not parent_widget.winfo_exists():
                    logging.debug(f"Skipped destroyed widget: {type(parent_widget).__name__}")
                    return
            except (tk.TclError, AttributeError):
                logging.debug(f"Skipped invalid widget: {type(parent_widget).__name__}")
                return
            
            # Check if current widget has an update_theme method
            if hasattr(parent_widget, 'update_theme') and callable(getattr(parent_widget, 'update_theme')):
                try:
                    parent_widget.update_theme()  # type: ignore
                    logging.debug(f"Called update_theme on {type(parent_widget).__name__}")
                except Exception as e:
                    logging.debug(f"Error calling update_theme on {type(parent_widget).__name__}: {e}")
            
            # Recursively check children
            try:
                children = parent_widget.winfo_children()
            except (tk.TclError, AttributeError):
                # Parent widget might be destroyed
                logging.debug(f"Cannot get children of destroyed widget: {type(parent_widget).__name__}")
                return
                
            for child in children:
                try:
                    # Double-check that child still exists before recursing
                    if hasattr(child, 'winfo_exists') and child.winfo_exists():
                        self._call_update_theme_methods(child)
                    else:
                        logging.debug(f"Skipped destroyed child widget: {type(child).__name__}")
                except (tk.TclError, AttributeError):
                    # Widget might be destroyed
                    logging.debug(f"Skipped invalid child widget: {type(child).__name__}")
                    pass
                    
        except Exception as e:
            logging.debug(f"Error calling update_theme methods: {e}")
    
    def _update_other_widgets(self, parent_widget: tk.Misc, bg_color: str, fg_color: str):
        """Update other widgets that might have hardcoded colors"""
        try:
            # Handle widgets that might have specific color properties that aren't updating
            for child in parent_widget.winfo_children():
                try:
                    # Update ALL Labels (not just those with explicit backgrounds)
                    if isinstance(child, tk.Label):
                        try:
                            # Always try to update Label colors
                            child.configure(bg=bg_color, fg=fg_color)
                            logging.debug(f"Updated Label widget colors")
                        except (tk.TclError, AttributeError):
                            pass
                    
                    # Update ALL Frames
                    elif isinstance(child, tk.Frame):
                        try:
                            # Always try to update Frame background
                            child.configure(bg=bg_color)
                            logging.debug(f"Updated Frame widget background")
                        except (tk.TclError, AttributeError):
                            pass                    # Update Canvas widgets and their contents
                    elif isinstance(child, tk.Canvas):
                        try:
                            child.configure(bg=bg_color)
                            # Also update canvas text items and other elements
                            try:
                                for item in child.find_all():
                                    try:
                                        item_type = str(child.type(item))
                                        if item_type == "text":
                                            child.itemconfig(item, fill=fg_color)                                        
                                        elif item_type == "rectangle":
                                            # Update rectangle fills if they're not transparent
                                            try:
                                                # Using type: ignore to suppress Pylance warning about itemcget return type
                                                current_fill = child.itemcget(item, "fill")  # type: ignore
                                                if current_fill and str(current_fill) not in ["", "none"]:  # type: ignore
                                                    child.itemconfig(item, fill=bg_color, outline=fg_color)
                                            except tk.TclError:
                                                pass                                        
                                        elif item_type == "oval":
                                            # Update oval fills similar to rectangles
                                            try:
                                                # Using type: ignore to suppress Pylance warning about itemcget return type
                                                current_fill = child.itemcget(item, "fill")  # type: ignore
                                                if current_fill and str(current_fill) not in ["", "none"]:  # type: ignore
                                                    child.itemconfig(item, fill=bg_color, outline=fg_color)
                                            except tk.TclError:
                                                pass
                                    except (tk.TclError, AttributeError, TypeError):
                                        # Skip items that can't be queried or updated
                                        continue
                            except (tk.TclError, AttributeError):
                                pass
                            logging.debug(f"Updated Canvas widget background and contents")
                        except (tk.TclError, AttributeError):
                            pass
                      # Update Listbox widgets
                    elif isinstance(child, tk.Listbox):
                        try:
                            child.configure(bg=bg_color, fg=fg_color, selectbackground=bg_color, selectforeground=fg_color)
                            logging.debug(f"Updated Listbox widget colors")
                        except (tk.TclError, AttributeError):
                            pass
                    
                    # Update Entry widgets
                    elif isinstance(child, tk.Entry):
                        try:
                            child.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)
                            logging.debug(f"Updated Entry widget colors")
                        except (tk.TclError, AttributeError):
                            pass
                    
                    # Update Message widgets
                    elif isinstance(child, tk.Message):
                        try:
                            child.configure(bg=bg_color, fg=fg_color)
                            logging.debug(f"Updated Message widget colors")
                        except (tk.TclError, AttributeError):
                            pass
                    
                    # Update Scale widgets
                    elif isinstance(child, tk.Scale):
                        try:
                            child.configure(bg=bg_color, fg=fg_color, activebackground=bg_color)
                            logging.debug(f"Updated Scale widget colors")
                        except (tk.TclError, AttributeError):
                            pass
                    
                    # Update Scrollbar widgets
                    elif isinstance(child, tk.Scrollbar):
                        try:
                            child.configure(bg=bg_color, activebackground=bg_color, troughcolor=bg_color)
                            logging.debug(f"Updated Scrollbar widget colors")
                        except (tk.TclError, AttributeError):
                            pass
                    
                    # Update Button widgets (tk.Button, not ttk.Button)
                    elif isinstance(child, tk.Button):
                        try:
                            child.configure(bg=bg_color, fg=fg_color, activebackground=bg_color, activeforeground=fg_color)
                            logging.debug(f"Updated Button widget colors")
                        except (tk.TclError, AttributeError):
                            pass                    # Force update ANY widget with a background option
                    else:
                        try:
                            # Try to update any widget that has background/foreground options
                            # Try both 'bg' and 'background' parameter names
                            try:
                                child.configure(bg=bg_color)  # type: ignore
                                logging.debug(f"Updated generic widget background (bg): {type(child).__name__}")
                            except (tk.TclError, AttributeError):
                                try:
                                    child.configure(background=bg_color)  # type: ignore
                                    logging.debug(f"Updated generic widget background (background): {type(child).__name__}")
                                except (tk.TclError, AttributeError):
                                    pass
                        except (tk.TclError, AttributeError):
                            pass
                        try:
                            # Try both 'fg' and 'foreground' parameter names
                            try:
                                child.configure(fg=fg_color)  # type: ignore
                                logging.debug(f"Updated generic widget foreground (fg): {type(child).__name__}")
                            except (tk.TclError, AttributeError):
                                try:
                                    child.configure(foreground=fg_color)  # type: ignore
                                    logging.debug(f"Updated generic widget foreground (foreground): {type(child).__name__}")
                                except (tk.TclError, AttributeError):
                                    pass
                        except (tk.TclError, AttributeError):
                            pass
                      # Recursively check children
                    self._update_other_widgets(child, bg_color, fg_color)
                    
                except tk.TclError:
                    # Widget might be destroyed
                    pass        
        except Exception as e:
            logging.debug(f"Error updating other widgets: {e}")

    def _update_ttk_widgets(self, bg_color: str, fg_color: str):
        """Update TTK widgets using theme styles to use appropriate colors"""
        try:
            style = ttk.Style()
            
            # Get a slightly different color for input field backgrounds
            # to differentiate them from the general background
            input_bg_color = self._get_input_background_color(bg_color)
            
            # Configure TTK widget styles with theme-appropriate colors
            # Use type: ignore to suppress Pylance warnings about style.configure
            
            # Basic widget styles
            style.configure('TLabel', background=bg_color, foreground=fg_color)  # type: ignore
            style.configure('TFrame', background=bg_color)  # type: ignore
            style.configure('TLabelFrame', background=bg_color, foreground=fg_color)  # type: ignore
            style.configure('TLabelFrame.Label', background=bg_color, foreground=fg_color)  # type: ignore            # Input widget styles - use special input background
            style.configure('TEntry', fieldbackground=input_bg_color, foreground=fg_color,  # type: ignore
                          insertcolor=fg_color)  # type: ignore
            style.configure('TSpinbox', fieldbackground=input_bg_color, foreground=fg_color, # type: ignore
                          insertcolor=fg_color)  # type: ignore            # Combobox needs special handling for its dropdown and input areas
            # Calculate subtle focus colors for combobox
            if self._is_dark_color(input_bg_color):
                # For dark input backgrounds: lighter focus selection
                combo_select_bg = self._lighten_color(input_bg_color, 0.2)
            else:
                # For light input backgrounds: darker focus selection
                combo_select_bg = self._darken_color(input_bg_color, 0.15)
                
            style.configure('TCombobox', fieldbackground=input_bg_color, foreground=fg_color, # type: ignore
                          background=bg_color, selectbackground=combo_select_bg, 
                          selectforeground=fg_color)  # type: ignore
            style.map('TCombobox',  # type: ignore
                fieldbackground=[('readonly', input_bg_color), ('!readonly', input_bg_color)],
                foreground=[('readonly', fg_color), ('!readonly', fg_color)],
                selectbackground=[('focus', combo_select_bg)],
                selectforeground=[('focus', fg_color)]
            )
              # Button styles with improved hover effects
            # Calculate subtle hover colors instead of full color swap
            if self._is_dark_color(bg_color):
                # For dark themes: lighter hover background
                hover_bg = self._lighten_color(bg_color, 0.2)
                pressed_bg = self._lighten_color(bg_color, 0.1)
            else:
                # For light themes: darker hover background
                hover_bg = self._darken_color(bg_color, 0.1)
                pressed_bg = self._darken_color(bg_color, 0.2)
            
            style.configure('TButton', background=bg_color, foreground=fg_color)  # type: ignore
            style.map('TButton',  # type: ignore
                background=[('active', hover_bg), ('pressed', pressed_bg)],
                foreground=[('active', fg_color), ('pressed', fg_color)]
            )            # Scrollbar and scale styles
            style.configure('TScrollbar', background=bg_color, troughcolor=bg_color,  # type: ignore
                          arrowcolor=fg_color)  # type: ignore
            style.configure('TScale', background=bg_color, foreground=fg_color,  # type: ignore
                          troughcolor=input_bg_color)  # type: ignore
            
            # Text widget styles
            style.configure('TText', background=input_bg_color, foreground=fg_color, # type: ignore
                          insertcolor=fg_color, selectbackground=fg_color,
                          selectforeground=bg_color)  # type: ignore
              # Treeview styles for better theme integration  
            style.configure('Treeview', background=input_bg_color, foreground=fg_color)  # type: ignore
            style.configure('Treeview.Heading', background=bg_color, foreground=fg_color)  # type: ignore
            
            # Calculate better selection colors for Treeview
            if self._is_dark_color(bg_color):
                # For dark themes: lighter selection background
                selection_bg = self._lighten_color(input_bg_color, 0.3)
            else:
                # For light themes: darker selection background  
                selection_bg = self._darken_color(input_bg_color, 0.2)
                
            style.map('Treeview',  # type: ignore
                background=[('selected', selection_bg)],
                foreground=[('selected', fg_color)]
            )
            
            # Notebook (tab) styles
            style.configure('TNotebook', background=bg_color)  # type: ignore
            style.configure('TNotebook.Tab', background=bg_color, foreground=fg_color)  # type: ignore
            style.map('TNotebook.Tab',  # type: ignore
                background=[('selected', bg_color), ('!selected', bg_color)],
                foreground=[('selected', fg_color), ('!selected', fg_color)]
            )
            
            # Progressbar to match theme
            style.configure('TProgressbar', background=fg_color, troughcolor=bg_color)  # type: ignore
            
            # Checkbutton and Radiobutton
            style.configure('TCheckbutton', background=bg_color, foreground=fg_color)  # type: ignore
            style.configure('TRadiobutton', background=bg_color, foreground=fg_color)  # type: ignore
            
            logging.debug(f"Updated TTK widget styles with theme colors: bg={bg_color}, fg={fg_color}, input_bg={input_bg_color}")
            
        except Exception as e:
            logging.warning(f"Failed to update TTK widget styles: {e}")
    
    def _get_input_background_color(self, bg_color: str) -> str:
        """Get a slightly different background color for input fields to make them stand out"""
        try:
            # For dark themes, make input fields slightly lighter
            # For light themes, make input fields slightly darker or keep them light
            is_dark = self._is_dark_color(bg_color)
            
            if is_dark:
                # For dark themes, lighten the background slightly for input fields
                if bg_color.startswith('#'):
                    # Convert hex to RGB, lighten by 20, convert back
                    hex_color = bg_color[1:]
                    if len(hex_color) == 6:
                        r = min(255, int(hex_color[0:2], 16) + 20)
                        g = min(255, int(hex_color[2:4], 16) + 20)
                        b = min(255, int(hex_color[4:6], 16) + 20)
                        return f"#{r:02x}{g:02x}{b:02x}"
                # Fallback for dark themes
                return '#404040'
            else:
                # For light themes, use white or very light background
                return 'white'
                
        except Exception:
            # Fallback - return the original background color
            return bg_color
    
    def reload_themes(self) -> int:
        """Forces a reload of all themes and returns the new count."""
        if not self._initialized or not self.root:
            logging.error("Cannot reload themes: ThemeManager not initialized.")
            return 0
            
        logging.info("Reloading themes...")
        # Reset lists
        self.available_themes = []
        self.loaded_custom_themes = set()
        # Re-initialize
        self._load_all_themes()
        return len(self.get_available_themes())

    def get_theme_colors(self) -> Dict[str, str]:
        """
        Get theme-appropriate colors for the current theme.
        Returns a dictionary with commonly used colors that adapt to the theme.
        Uses caching for better performance.
        """
        if not self._initialized or not self.root:
            # Return safe defaults if not initialized
            return {
                'foreground': 'black',
                'background': 'white',
                'text_valid': 'black',
                'text_error': 'red',
                'text_info': 'blue',
                'text_success': 'green',
                'text_warning': 'orange'
            }
            
        # Get current theme for cache key
        try:
            style = ttk.Style()
            current_theme = str(style.theme_use())
            
            # Check cache first
            if current_theme in self._theme_colors_cache:
                return self._theme_colors_cache[current_theme].copy()
                
        except Exception:
            current_theme = 'unknown'
            
        try:
            style = ttk.Style()
            # Get the default label colors from current theme
            # Note: Tkinter's style.lookup returns dynamic types, so we need type ignores
            try:
                label_fg_raw = style.lookup('TLabel', 'foreground')  # type: ignore
                label_bg_raw = style.lookup('TLabel', 'background')  # type: ignore
                
                # Safely convert to strings with fallbacks
                label_fg: str = str(label_fg_raw) if label_fg_raw else 'black'  # type: ignore
                label_bg: str = str(label_bg_raw) if label_bg_raw else 'white'  # type: ignore
                
            except Exception:
                # Fallback if style lookup fails
                label_fg = 'black'
                label_bg = 'white'
            
            # Detect if theme is dark or light based on background
            is_dark_theme = self._is_dark_color(label_bg)
            
            if is_dark_theme:
                colors = {
                    'foreground': label_fg or 'white',
                    'background': label_bg or '#2d2d2d',
                    'text_valid': '#90EE90',  # Light green for dark themes
                    'text_error': '#FF6B6B',  # Light red for dark themes
                    'text_info': '#87CEEB',   # Light blue for dark themes
                    'text_success': '#98FB98', # Pale green for dark themes
                    'text_warning': '#FFD700'  # Gold for dark themes
                }
            else:
                colors = {
                    'foreground': label_fg or 'black',
                    'background': label_bg or 'white',
                    'text_valid': '#006400',  # Dark green for light themes
                    'text_error': '#DC143C',  # Dark red for light themes
                    'text_info': '#0000CD',   # Medium blue for light themes
                    'text_success': '#228B22', # Forest green for light themes
                    'text_warning': '#FF8C00'  # Dark orange for light themes
                }
            
            # Cache the result for future use
            self._theme_colors_cache[current_theme] = colors.copy()
            return colors
                
        except Exception as e:
            logging.warning(f"Could not determine theme colors: {e}")
            # Return safe defaults
            default_colors = {
                'foreground': 'black',
                'background': 'white',
                'text_valid': 'black',
                'text_error': 'red',
                'text_info': 'blue',
                'text_success': 'green',
                'text_warning': 'orange'
            }
            # Cache the default too
            self._theme_colors_cache[current_theme] = default_colors.copy()
            return default_colors
    
    def _is_dark_color(self, color_str: str) -> bool:
        """
        Determine if a color string represents a dark color.
        Returns True if the color is dark, False if light.
        """
        if not color_str or color_str in ['', 'None']:
            return False
            
        try:
            # Handle common color names
            color_map = {
                'black': (0, 0, 0),
                'white': (255, 255, 255),
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'gray': (128, 128, 128),
                'grey': (128, 128, 128),
            }
            
            color_lower = color_str.lower()
            if color_lower in color_map:
                r, g, b = color_map[color_lower]
            elif color_str.startswith('#'):
                # Handle hex colors
                hex_color = color_str[1:]
                if len(hex_color) == 3:
                    # Short hex format #rgb
                    r = int(hex_color[0] * 2, 16)
                    g = int(hex_color[1] * 2, 16)
                    b = int(hex_color[2] * 2, 16)
                elif len(hex_color) == 6:
                    # Long hex format #rrggbb
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                else:
                    return False
            else:
                # Try to get RGB values from Tkinter
                if self.root:
                    try:
                        rgb = self.root.winfo_rgb(color_str)
                        # winfo_rgb returns values in range 0-65535, convert to 0-255
                        r = rgb[0] // 256
                        g = rgb[1] // 256
                        b = rgb[2] // 256
                    except tk.TclError:
                        return False
                else:
                    return False
            
            # Calculate perceived brightness using weighted RGB
            # Formula: 0.299*R + 0.587*G + 0.114*B
            brightness = (0.299 * r + 0.587 * g + 0.114 * b)
            
            # Consider colors with brightness < 128 as dark
            return brightness < 128
            
        except (ValueError, IndexError):
            return False
    
    def get_adaptive_color(self, color_type: str) -> str:
        """
        Get a specific adaptive color for the current theme.
        
        Args:
            color_type: One of 'foreground', 'background', 'text_valid', 
                       'text_error', 'text_info', 'text_success', 'text_warning'
        
        Returns:
            Color string appropriate for the current theme
        """
        colors = self.get_theme_colors()
        return colors.get(color_type, colors['foreground'])

    def _lighten_color(self, color_str: str, factor: float) -> str:
        """
        Lighten a color by a given factor.
        
        Args:
            color_str: Color string (hex, name, etc.)
            factor: Factor to lighten by (0.0-1.0)
        
        Returns:
            Lightened color as hex string
        """
        try:
            if not self.root:
                return color_str
                
            # Convert color to RGB
            rgb = self.root.winfo_rgb(color_str)
            # winfo_rgb returns values in range 0-65535, convert to 0-255
            r = rgb[0] // 256
            g = rgb[1] // 256
            b = rgb[2] // 256
            
            # Lighten by moving towards white
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (tk.TclError, ValueError, AttributeError):
            return color_str
    
    def _darken_color(self, color_str: str, factor: float) -> str:
        """
        Darken a color by a given factor.
        
        Args:
            color_str: Color string (hex, name, etc.)
            factor: Factor to darken by (0.0-1.0)
        
        Returns:
            Darkened color as hex string
        """
        try:
            if not self.root:
                return color_str
                
            # Convert color to RGB
            rgb = self.root.winfo_rgb(color_str)
            # winfo_rgb returns values in range 0-65535, convert to 0-255
            r = rgb[0] // 256
            g = rgb[1] // 256
            b = rgb[2] // 256
            
            # Darken by moving towards black
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (tk.TclError, ValueError, AttributeError):
            return color_str

# Singleton instance (now uninitialized until app calls initialize())
theme_manager = ThemeManager()
