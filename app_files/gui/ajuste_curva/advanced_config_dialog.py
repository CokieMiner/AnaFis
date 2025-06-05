"""Advanced configuration dialog for curve fitting"""
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from app_files.utils.constants import TRANSLATIONS

# Import for type hints only
if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
    from app_files.gui.ajuste_curva.adjustment_points_manager import AdjustmentPointsManager
    from app_files.gui.ajuste_curva.parameter_estimates_manager import ParameterEstimatesManager  
    from app_files.gui.ajuste_curva.custom_function_manager import CustomFunctionManager

class AdvancedConfigDialog:
    """Dialog for advanced configuration options"""
    
    def __init__(self, parent_frame: 'AjusteCurvaFrame', adjustment_points_manager: 'AdjustmentPointsManager', 
                 parameter_estimates_manager: 'ParameterEstimatesManager', 
                 custom_function_manager: 'CustomFunctionManager', language: str = 'pt') -> None:
        """Initialize the advanced configuration dialog
        
        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this dialog
            adjustment_points_manager: Manager for adjustment points
            parameter_estimates_manager: Manager for parameter estimates
            custom_function_manager: Manager for custom functions
            language: Interface language
        """
        self.parent = parent_frame
        self.language = language
        
        # Store manager references
        self.adjustment_points_manager = adjustment_points_manager
        self.parameter_estimates_manager = parameter_estimates_manager
        self.custom_function_manager = custom_function_manager
    
    def show_dialog(self) -> None:
        """Show the advanced configuration dialog"""
        # Create a new top-level window
        popup = tk.Toplevel(self.parent.parent)
        popup.title(TRANSLATIONS[self.language].get('advanced_config', 'Configurações avançadas'))
        popup.geometry("500x600")
        popup.resizable(True, True)
        
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
        self.adjustment_points_manager.setup_ui(adjust_tab, maximize_scrollbox=True)
        
        # === Second tab: Initial Estimates ===
        estimates_tab = ttk.Frame(notebook)
        notebook.add(estimates_tab, text=TRANSLATIONS[self.language].get('initial_estimates', 'Estimativas iniciais'))
        
        # Set up the parameter estimates UI
        self.parameter_estimates_manager.setup_ui(estimates_tab)
        
        # === Third tab: Custom Functions ===
        funcs_tab = ttk.Frame(notebook)
        notebook.add(funcs_tab, text=TRANSLATIONS[self.language].get('custom_functions', 'Funções personalizadas'))
        
        # Configure grid weights for custom functions tab
        funcs_tab.columnconfigure(0, weight=1)
        funcs_tab.rowconfigure(1, weight=1)  # Make the row with scrollbox expandable
        
        # Set up the custom functions UI with expanded scrollbox
        self.custom_function_manager.setup_ui(funcs_tab, maximize_scrollbox=True)
          # Function to handle popup closing
        def on_close() -> None:
            # Save adjustment points when closing
            self.adjustment_points_manager.save_points()
            # Save custom functions
            self.custom_function_manager.save_functions()
            # Destroy the popup
            popup.destroy()
        
        # Button to close the popup - now calls our custom close function
        close_button = ttk.Button(popup, text=TRANSLATIONS[self.language].get('close', 'Fechar'),
                  command=on_close)
        close_button.pack(pady=10)
        
        # Also handle window close via X button
        popup.protocol("WM_DELETE_WINDOW", on_close)
        
        # Center the popup on the parent window
        popup.update_idletasks()
        parent_window = self.parent.parent
        x = parent_window.winfo_x() + (parent_window.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = parent_window.winfo_y() + (parent_window.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")