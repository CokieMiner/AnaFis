"""Parameter estimation UI for curve fitting"""
import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
from typing import TYPE_CHECKING, Dict, List, Any

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame

class ParameterEstimatesManager:
    """Manages parameter estimates for curve fitting"""
    
    def __init__(self, parent_frame: 'AjusteCurvaFrame', language: str = 'pt') -> None:
        """Initialize the parameter estimates manager
        
        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this manager
            language: Interface language
        """
        self.parent = parent_frame
        self.language = language
        
        # Dictionary to store parameter entry widgets
        self.param_entries = {}
        
        # Parameters list
        self.parameters = []
        
    def create_estimates_frame(self, parent_frame: tk.Widget) -> ttk.LabelFrame:
        """Create the estimates frame that will be used in popup
        
        Args:
            parent_frame: Parent frame for the estimates widgets
        
        Returns:
            ttk.LabelFrame: The estimates frame
        """
        # Create estimates frame
        self.estimates_frame = ttk.LabelFrame(parent_frame, text=TRANSLATIONS[self.language]['initial_estimates'])
        return self.estimates_frame
    
    def setup_ui(self, tab: tk.Widget) -> None:
        """Set up UI elements in the given tab
        
        Args:
            tab: The tab frame to add UI elements to
        """
        tab.columnconfigure(0, weight=1)
        
        # Initial estimates controls
        ttk.Label(tab, text=TRANSLATIONS[self.language].get('initial_values', 'Valores iniciais:')).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Create initial parameter entries dynamically
        param_frame = ttk.Frame(tab)
        param_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        tab.rowconfigure(1, weight=1)
        
        # Add existing parameter fields if available
        if self.param_entries:
            for i, (param_name, entry) in enumerate(self.param_entries.items()):
                ttk.Label(param_frame, text=f"{param_name}:").grid(
                    row=i, column=0, sticky="w", padx=5, pady=2)
                
                # Create a new entry in the popup that mirrors the main one
                popup_entry = ttk.Entry(param_frame, width=10)
                popup_entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                popup_entry.insert(0, entry.get())  # Copy current value
                
                # Make the popup entry update the main entry when changed
                def update_main_entry(event, param=param_name, popup_widget=popup_entry):
                    self.param_entries[param].delete(0, tk.END)
                    self.param_entries[param].insert(0, popup_widget.get())
                
                popup_entry.bind("<FocusOut>", update_main_entry)
    
    def update_estimates_frame(self, equation):
        """Update the estimates frame based on the equation
        
        Args:
            equation: The equation string to extract parameters from
        """
        # Clear current frame
        for widget in self.estimates_frame.winfo_children():
            widget.destroy()
            
        self.param_entries = {}  # Reset the parameter entries dictionary

        try:
            # Process equation
            equation = equation.replace('^', '**')
            if '=' in equation:
                equation = equation.split('=')[1].strip()

            # Extract parameters
            self.parameters = self.extract_parameters(equation)

            # Create input fields for each parameter
            for i, param in enumerate(self.parameters):
                ttk.Label(self.estimates_frame, text=f"{param}:").grid(row=i, column=0, padx=5, pady=2)
                entry = ttk.Entry(self.estimates_frame, width=10)
                entry.insert(0, "1.0")
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.param_entries[str(param)] = entry  # Store in dictionary
                # For compatibility with existing code
                setattr(self.parent, f"estimate_{param}", entry)
        except Exception as e:
            messagebox.showerror(
                TRANSLATIONS[self.language]['error'],
                TRANSLATIONS[self.language]['invalid_formula'].format(error=str(e))
            )
    
    def extract_parameters(self, equation):
        """Extract parameters from equation
        
        Args:
            equation: Equation string
            
        Returns:
            List of symbols representing parameters
        """
        try:
            # Parse the equation with sympy
            expr = sp.sympify(equation)
            
            # Find all symbols in the expression
            symbols = list(expr.free_symbols)
            
            # Filter out 'x' which is the independent variable
            parameters = [sym for sym in symbols if sym.name != 'x']
            
            return parameters
        except Exception as e:
            print(f"Error extracting parameters: {str(e)}")
            return []
    
    def get_initial_estimates(self):
        """Get initial parameter estimates
        
        Returns:
            List of parameter values
        """
        estimates = []
        for param in self.parameters:
            entry = self.param_entries.get(str(param))
            if entry:
                try:
                    estimates.append(float(entry.get()))
                except ValueError:
                    estimates.append(1.0)  # Default if invalid value
        return estimates