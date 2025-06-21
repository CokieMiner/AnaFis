"""Advanced configuration dialog for curve fitting"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import TYPE_CHECKING, Optional
import logging

from app_files.utils.constants import TRANSLATIONS

# Import for type hints only
if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
    from app_files.gui.ajuste_curva.adjustment_points_manager import AdjustmentPointsManager
    from app_files.gui.ajuste_curva.parameter_estimates_manager import ParameterEstimatesManager  
    from app_files.gui.ajuste_curva.custom_function_manager import CustomFunctionManager

class AdvancedConfigDialog:
    """Dialog for advanced configuration options"""
    
    def __init__(self, parent_frame: 'AjusteCurvaFrame', 
             custom_function_manager: Optional['CustomFunctionManager'],
             parameter_estimates_manager: Optional['ParameterEstimatesManager'],
             adjustment_points_manager: Optional['AdjustmentPointsManager'],
             language: str = 'pt') -> None:
        """Initialize the advanced configuration dialog
        
        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this dialog
            custom_function_manager: Manager for custom functions
            parameter_estimates_manager: Manager for parameter estimates
            adjustment_points_manager: Manager for adjustment points
            language: Interface language        """
        self.parent = parent_frame
        self.language = language
        self.dialog = None
        self.custom_function_manager = custom_function_manager
        self.parameter_estimates_manager = parameter_estimates_manager
        self.adjustment_points_manager = adjustment_points_manager  # Store the manager
    
    def show_dialog(self) -> None:
        """Show the advanced configuration dialog"""
        # Create a new top-level window
        popup = tk.Toplevel(self.parent.parent)
        popup.title(TRANSLATIONS[self.language].get('advanced_config', 'Configurações avançadas'))
        popup.geometry("620x670")  # Increased width by 10px more (585->595, kept height at 650)
        popup.resizable(True, True)
          # Apply theme-adaptive background
        from app_files.utils.theme_manager import theme_manager
        popup.configure(bg=theme_manager.get_adaptive_color('background'))
        
        # Store reference to popup for theme updates
        self.popup_window = popup
        
        # Register for theme change callbacks
        theme_manager.register_color_update_callback(self._update_popup_colors)
        
        # Fix the transient call by checking if parent is a window
        if isinstance(self.parent.parent, (tk.Tk, tk.Toplevel)):
            popup.transient(self.parent.parent)  # Make it a child of main window
        
        popup.grab_set()  # Make it modal
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(popup)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === First tab: Adjustment Points ===
        adjust_tab = ttk.Frame(notebook)
        notebook.add(adjust_tab, text=TRANSLATIONS[self.language].get('adjustment_points', 'Pontos de ajuste'))
        
        # Configure grid weights to maximize scrollbox space
        adjust_tab.columnconfigure(0, weight=1)
        adjust_tab.rowconfigure(1, weight=1)  # Make the row with scrollbox expandable
        
        # Set up the adjustment points UI with expanded scrollbox
        if self.adjustment_points_manager is None:
            logging.error("adjustment_points_manager is None, cannot set up UI")
            messagebox.showerror(  # type: ignore
                TRANSLATIONS[self.language].get('error', 'Error'), 
                TRANSLATIONS[self.language].get('config_error_adjust_manager', 'Configuration error: adjustment points manager not initialized')
            )
            return
            
        self.adjustment_points_manager.setup_ui(adjust_tab, maximize_scrollbox=True)
        
        # === Second tab: Initial Estimates ===
        estimates_tab = ttk.Frame(notebook)
        notebook.add(estimates_tab, text=TRANSLATIONS[self.language].get('initial_estimates', 'Estimativas iniciais'))
        
        # Add a safety check before calling setup_ui
        if self.parameter_estimates_manager is None:
            logging.error("parameter_estimates_manager is None, cannot set up UI")
            messagebox.showerror(  # type: ignore
                TRANSLATIONS[self.language].get('error', 'Error'), 
                TRANSLATIONS[self.language].get('config_error_param_manager', 'Configuration error: parameter estimates manager not initialized')
            )
            return
            
        # Set up the parameter estimates UI
        self.parameter_estimates_manager.setup_ui(estimates_tab)
        
        # === Third tab: Custom Functions ===
        funcs_tab = ttk.Frame(notebook)
        notebook.add(funcs_tab, text=TRANSLATIONS[self.language].get('custom_functions', 'Funções personalizadas'))
        
        # Configure grid weights for custom functions tab
        funcs_tab.columnconfigure(0, weight=1)
        funcs_tab.rowconfigure(1, weight=1)  # Make the row with scrollbox expandable
        
        # Set up the custom functions UI with expanded scrollbox
        if self.custom_function_manager is None:
            logging.error("custom_function_manager is None, cannot set up UI")
            messagebox.showerror(  # type: ignore
                TRANSLATIONS[self.language].get('error', 'Error'), 
                TRANSLATIONS[self.language].get('config_error_custom_func', 'Configuration error: custom function manager not initialized')
            )
            return
            
        self.custom_function_manager.setup_ui(funcs_tab, maximize_scrollbox=True)
        
        # Function to handle popup closing
        def on_close() -> None:
            # Save adjustment points when closing
            if self.adjustment_points_manager is not None:
                self.adjustment_points_manager.save_points()
            # Save custom functions
            if self.custom_function_manager is not None:
                self.custom_function_manager.save_functions()
            # Destroy the popup
            popup.destroy()
          # Button to close the popup - now calls our custom close function
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10, fill='x')
        
        close_button = ttk.Button(button_frame, text=TRANSLATIONS[self.language].get('close', 'Fechar'),
                  command=on_close)
        close_button.pack(anchor='center')
        
        # Also handle window close via X button
        popup.protocol("WM_DELETE_WINDOW", on_close)
        
        # Center the popup on the parent window
        popup.update_idletasks()
        parent_window = self.parent.parent
        x = parent_window.winfo_x() + (parent_window.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = parent_window.winfo_y() + (parent_window.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
    def _update_popup_colors(self) -> None:
        """Update popup colors when theme changes"""
        try:
            if hasattr(self, 'popup_window') and self.popup_window.winfo_exists():
                from app_files.utils.theme_manager import theme_manager
                bg_color = theme_manager.get_adaptive_color('background')
                self.popup_window.configure(bg=bg_color)
                logging.debug("Advanced config dialog colors updated for theme change")
        except Exception as e:
            logging.warning(f"Failed to update advanced config dialog colors: {e}")
