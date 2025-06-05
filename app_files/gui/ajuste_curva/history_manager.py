"""History manager for curve fitting results"""
from tkinter import ttk

from app_files.utils.constants import TRANSLATIONS

class HistoryManager:
    """Manages history of curve fitting results"""
    
    def __init__(self, parent_frame, language='pt'):
        """Initialize the history manager
        
        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this manager
            language: Interface language
        """
        self.parent = parent_frame
        self.language = language
        
        # History state
        self.history = []
        self.history_index = -1
        
        # UI elements
        self.history_label = None

    def setup_ui(self, parent_frame):
        """Set up history navigation UI

        Args: 
            parent_frame: Parent frame for the history widgets
        """
        # History navigation frame
        nav_frame = ttk.Frame(parent_frame)
        nav_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        prev_button = ttk.Button(nav_frame, text=" Anterior", command=self.prev_fit)
        prev_button.grid(row=0, column=0, padx=2)
        
        next_button = ttk.Button(nav_frame, text="Próximo ", command=self.next_fit)
        next_button.grid(row=0, column=1, padx=2)
        
        self.history_label = ttk.Label(nav_frame, text="Histórico: 0/0")
        self.history_label.grid(row=0, column=2, padx=10, sticky="w")
        
        # Configure column weights
        nav_frame.columnconfigure(3, weight=1)  # Add empty column with weight to push buttons left
    
    def add_fit_result(self, result, chi2, r2, equation, parameters):
        """Add a new fit result to history
        
        Args:
            result: The fit result object
            chi2: Chi-squared value
            r2: R-squared value
            equation: The equation used for the fit
            parameters: List of parameters
        """
        fit_data = {
            'result': result,
            'chi2': chi2,
            'r2': r2,
            'equation': equation,
            'parameters': parameters
        }
        self.history.append(fit_data)
        self.history_index = len(self.history) - 1
        self.update_history_label()
    
    def prev_fit(self):
        """Navigate to previous fit in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.apply_fit_from_history()
            
    def next_fit(self):
        """Navigate to next fit in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.apply_fit_from_history()
    
    def apply_fit_from_history(self):
        """Apply fit from history"""
        if 0 <= self.history_index < len(self.history):
            fit_data = self.history[self.history_index]
            
            # Update parent with historical data
            self.parent.last_result = fit_data['result']
            self.parent.last_chi2 = fit_data['chi2']
            self.parent.last_r2 = fit_data['r2']
            self.parent.equacao = fit_data['equation']
            self.parent.parametros = fit_data['parameters']
            
            # Display results
            self.parent.mostrar_resultados(self.parent.last_result)
            self.update_history_label()
            
    def update_history_label(self):
        """Update history navigation label"""
        if self.history_label:
            total = len(self.history)
            current = self.history_index + 1 if total > 0 else 0
            self.history_label.config(text=f"Histórico: {current}/{total}")