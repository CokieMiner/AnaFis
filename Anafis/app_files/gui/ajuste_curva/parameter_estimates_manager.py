"""Parameter estimation UI for curve fitting"""
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
from typing import TYPE_CHECKING, Dict, List, cast

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING:
    # from tkinter import Event # Keep or change based on usage - We are using tk.Event now
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame

class ParameterEstimatesManager:
    """Manages parameter estimates for curve fitting"""
    parent: 'AjusteCurvaFrame'
    language: str
    param_entries: Dict[str, ttk.Entry]
    parameters: List[sp.Symbol]
    estimates_frame: ttk.LabelFrame # Added type hint for estimates_frame
    
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
                def update_main_entry(event: tk.Event, param: str = param_name, popup_widget: ttk.Entry = popup_entry) -> None: # Changed tk.Event to tk.Event[Any]
                    main_entry = self.param_entries[param]
                    main_entry.delete(0, tk.END)
                    main_entry.insert(0, popup_widget.get())
                
                popup_entry.bind("<FocusOut>", update_main_entry)
    
    def update_estimates_frame(self, equation: str) -> None: # Added type hint for equation and return
        """Update the estimates frame based on the equation
        
        Args:
            equation: The equation string to extract parameters from
        """
        # Clear current frame
        for widget in self.estimates_frame.winfo_children():
            widget.destroy()
            
        # Reset the parameter entries dictionary
        self.param_entries = {}

        try:
            # Process equation
            equation = equation.replace('^', '**')
            if '=' in equation:
                equation = equation.split('=')[1].strip()

            # Extract parameters
            self.parameters = self.extract_parameters(equation)

            # Create input fields for each parameter
            for i, param_sym in enumerate(self.parameters): # Renamed param to param_sym for clarity
                param_name: str = str(param_sym) # Explicitly convert symbol to string for key
                ttk.Label(self.estimates_frame, text=f"{param_name}:").grid(row=i, column=0, padx=5, pady=2)
                entry = ttk.Entry(self.estimates_frame, width=10)
                entry.insert(0, "1.0")
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.param_entries[param_name] = entry  # Store in dictionary
                # For compatibility with existing code
                setattr(self.parent, f"estimate_{param_name}", entry)
        except Exception as e:
            messagebox.showerror( # type: ignore[reportUnknownMemberType]
                TRANSLATIONS[self.language]['error'],
                TRANSLATIONS[self.language]['invalid_formula'].format(error=str(e))
            )
    
    def extract_parameters(self, equation: str) -> List[sp.Symbol]: # Added type hint for equation and return
        """Extract parameters from equation
        
        Args:
            equation: Equation string
            
        Returns:
            List of symbols representing parameters
        """
        try:
            # Parse the equation with sympy
            # Add type ignore for sympify and free_symbols as Pylance struggles with their complex types
            expr: sp.Expr = cast(sp.Expr, sp.sympify(equation)) # type: ignore[reportUnknownMemberType]
            
            # Find all symbols in the expression
            symbols: List[sp.Symbol] = list(cast(set[sp.Symbol], expr.free_symbols)) # type: ignore[reportUnknownMemberType]
              # Filter out 'x' which is the independent variable
            parameters_out: List[sp.Symbol] = [sym for sym in symbols if sym.name != 'x'] # Renamed parameters to parameters_out
            
            return parameters_out
        
        except Exception as e:
            logging.error(f"Error extracting parameters: {str(e)}")
            return []
    
    def get_initial_estimates(self) -> List[float]: # Added type hint for return
        """Get initial parameter estimates
        
        Returns:
            List of parameter values
        """
        estimates: List[float] = []
        for param_sym in self.parameters: # Renamed param to param_sym for clarity
            param_name: str = str(param_sym) # Explicitly convert symbol to string for key
            entry = self.param_entries.get(param_name)
            if entry:
                try:
                    estimates.append(float(entry.get()))
                except ValueError:
                    estimates.append(1.0)  # Default if invalid value
            else: # Handle case where entry might not exist, though unlikely with current logic
                estimates.append(1.0)
        return estimates
