"""Custom function management for curve fitting"""
import tkinter as tk
import numpy as np
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Tuple, List, Optional
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame

class CustomFunctionManager:
    """Manages custom functions added to the plot"""
    
    def __init__(self, parent_frame: 'AjusteCurvaFrame', ax: Axes, canvas: FigureCanvasTkAgg, language: str = 'pt') -> None:
        """Initialize the function manager
        
        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this manager
            ax: The matplotlib axis to plot functions on
            canvas: The matplotlib canvas for drawing
            language: Interface language
        """
        self.parent = parent_frame
        self.ax = ax
        self.canvas = canvas
        self.language = language
        
        # Storage for custom functions and their plot lines
        self.custom_functions: List[Tuple[str, str]] = []  # List of (function_text, color) pairs
        self.custom_function_lines: List[Line2D] = []  # List of matplotlib Line2D objects
        
        # UI elements initialized in setup_ui
        self.functions_list: Optional[tk.Listbox] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None
        self.func_entry: Optional[ttk.Entry] = None
        self.color_var: Optional[tk.StringVar] = None
        
    def setup_ui(self, parent_frame: tk.Widget, maximize_scrollbox: bool = False) -> None:
        """Set up UI elements in the given parent frame
        
        Args:
            parent_frame: Frame to place the UI elements in
            maximize_scrollbox: Whether to maximize the scrollbox size
        """
        # Configure parent to allow expansion
        parent_frame.columnconfigure(0, weight=1)
        
        # Instruction label
        ttk.Label(parent_frame, text=TRANSLATIONS[self.language].get('custom_funcs_desc', 
                                                         'Adicione funções para mostrar no gráfico:')).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Create scrollable frame for functions
        functions_frame = ttk.Frame(parent_frame)
        functions_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        if maximize_scrollbox:
            # Configure to maximize functions list
            parent_frame.rowconfigure(1, weight=1)  # Let the scrollbox expand vertically
        
        # Frame for function management
        func_frame = ttk.Frame(functions_frame)
        func_frame.pack(fill=tk.BOTH, expand=True)
        func_frame.columnconfigure(0, weight=1)
        func_frame.rowconfigure(0, weight=1)  # Allow list to expand vertically
        
        # List of functions with increased height when maximized
        list_height = 12 if maximize_scrollbox else 6
        self.functions_list = tk.Listbox(func_frame, height=list_height)
        self.functions_list.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add scrollbar to functions list
        self.scrollbar = ttk.Scrollbar(func_frame, orient="vertical", command=self.functions_list.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.functions_list.configure(yscrollcommand=self.scrollbar.set)
        
        # Load existing functions if any
        for func in self.custom_functions:
            func_text, color = func
            self.functions_list.insert(tk.END, f"{func_text} [{color}]")
                
        # Function input frame
        input_frame = ttk.Frame(parent_frame)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        # Function input field
        ttk.Label(input_frame, text="y =").grid(row=0, column=0, padx=5, pady=5)
        self.func_entry = ttk.Entry(input_frame)
        self.func_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Color selection
        ttk.Label(input_frame, text=TRANSLATIONS[self.language].get('color', "Cor:")).grid(
            row=1, column=0, padx=5, pady=5)
        self.color_var = tk.StringVar(value="red")
        color_combo = ttk.Combobox(input_frame, textvariable=self.color_var, 
                                 values=["red", "green", "blue", "orange", "purple", "black"],
                                 state="readonly", width=10)
        color_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
          
        # Buttons frame
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        # Configure button frame columns
        buttons_frame.columnconfigure(0, weight=0)
        buttons_frame.columnconfigure(1, weight=0)
        buttons_frame.columnconfigure(2, weight=1)
        buttons_frame.columnconfigure(3, weight=0)
        
        # Add function button
        add_button = ttk.Button(buttons_frame, text=TRANSLATIONS[self.language].get('add', "Adicionar"),
                              command=self.add_function)
        add_button.grid(row=0, column=0, padx=5)
        
        # Remove function button
        remove_button = ttk.Button(buttons_frame, text=TRANSLATIONS[self.language].get('remove', "Remover"),
                                command=self.remove_function)
        remove_button.grid(row=0, column=1, padx=5)
        
        # Preview function button
        preview_button = ttk.Button(buttons_frame, text=TRANSLATIONS[self.language].get('preview', "Visualizar"),
                                  command=self.preview_functions)
        preview_button.grid(row=0, column=3, padx=5, sticky="e")
    
    def add_function(self) -> None:
        """Add a custom function to the plot"""
        if self.func_entry is None:
            return
            
        function_text = self.func_entry.get().strip()
        if not function_text:
            messagebox.showwarning(
                TRANSLATIONS[self.language].get('warning', "Aviso"), 
                "Por favor, insira uma função válida."
            )
            return
            
        # Create a displayable function entry with color information
        color = self.color_var.get() if self.color_var else "red"
        display_text = f"{function_text} [{color}]"
        
        # Store the function
        self.custom_functions.append((function_text, color))
        
        # Add to listbox
        if self.functions_list:
            self.functions_list.insert(tk.END, display_text)
        
        # Clear entry
        self.func_entry.delete(0, tk.END)
        
        # Preview if data exists
        self.preview_functions()
    
    def remove_function(self) -> None:
        """Remove selected function from the list"""
        if self.functions_list is None:
            return
            
        selected = self.functions_list.curselection()
        if not selected:
            messagebox.showwarning(
                TRANSLATIONS[self.language].get('warning', "Aviso"), 
                "Selecione uma função para remover."
            )
            return
            
        # Get index of selected item
        idx = int(selected[0])
        
        # Remove from listbox
        self.functions_list.delete(idx)
        
        # Remove from storage
        if idx < len(self.custom_functions):
            self.custom_functions.pop(idx)
        
        # Remove from plot if present
        if idx < len(self.custom_function_lines):
            line = self.custom_function_lines.pop(idx)
            if line in self.ax.lines:
                line.remove()
        
        # Redraw the plot with updated functions - this will automatically update the axes
        self.update_plot()
    
    def preview_functions(self) -> None:
        """Preview custom functions on the plot"""
        # Get x data from parent
        if not hasattr(self.parent, 'x') or len(self.parent.x) == 0:
            messagebox.showinfo(
                TRANSLATIONS[self.language].get('info', "Informação"), 
                "Carregue dados primeiro para visualizar as funções."
            )
            return
        
        # Use the common plotting function
        self.update_plot()
    def update_plot(self) -> None:
        """Update the plot with custom functions and refresh axes"""
        # Get x data from parent
        if not hasattr(self.parent, 'x') or len(self.parent.x) == 0:
            return
        
        x_data = self.parent.x
        y_data = self.parent.y
        
        # Clear old function lines
        for line in self.custom_function_lines:
            if line in self.ax.lines:
                line.remove()
        self.custom_function_lines = []
        
        # Generate x values for functions (use higher density than data)
        # Cast to float to avoid numpy type issues
        x_min, x_max = float(np.min(x_data)), float(np.max(x_data))
        x_range = np.linspace(x_min, x_max, 1000)
        
        # Get current y data range to determine if we need to update axes
        y_min: float = float('inf')
        y_max: float = float('-inf')
        
        # Consider data points for y-range
        if len(y_data) > 0:
            data_y_min = float(np.min(y_data))
            data_y_max = float(np.max(y_data))
            y_min = min(y_min, data_y_min)
            y_max = max(y_max, data_y_max)
        
        # Plot each function and track min/max y values
        for func_text, color in self.custom_functions:
            try:
                # Convert function text to executable code
                func_expr = func_text.replace("^", "**")
                
                # Evaluate function for each x value
                y_values: List[float] = []
                for x_val in x_range:
                    try:
                        # Cast x to float to avoid numpy type issues
                        x = float(x_val)
                        y = eval(func_expr, {"x": x, "np": np, "sin": np.sin, "cos": np.cos, 
                                             "tan": np.tan, "exp": np.exp, "log": np.log,
                                             "sqrt": np.sqrt, "pi": np.pi})
                        y_values.append(float(y))
                    except:
                        y_values.append(float('nan'))  # Use NaN for invalid values
                
                # Update y-range
                valid_y = [y for y in y_values if not np.isnan(y) and not np.isinf(y)]
                if valid_y:
                    func_y_min = min(valid_y)
                    func_y_max = max(valid_y)
                    y_min = min(y_min, func_y_min)
                    y_max = max(y_max, func_y_max)
                
                # Plot the function
                line, = self.ax.plot(x_range, y_values, color=color, linestyle="--", alpha=0.7, linewidth=1.5)
                self.custom_function_lines.append(line)
            
            except Exception as e:
                print(f"Error processing function '{func_text}': {str(e)}")
        
        # Update axes if needed
        if y_min != float('inf') and y_max != float('-inf'):
            # Add 10% padding to y-axis
            y_padding = (y_max - y_min) * 0.1
            self.ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        # Force tight layout and update canvas
        if hasattr(self.parent, 'plot_manager'):
            self.parent.plot_manager.fig.tight_layout()
        self.canvas.draw()    
        
    def save_functions(self) -> None:
        """Save the custom functions"""
        # Save the functions to the parent if it has the appropriate method
        if hasattr(self.parent, 'update_custom_functions'):
            self.parent.update_custom_functions(self.custom_functions)