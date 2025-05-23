# Standard library imports
import os
import logging
import re
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Third-party imports
import numpy as np
import sympy as sp
import pandas as pd
from scipy.odr import ODR, Model, RealData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Tkinter imports
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText

class ErrorHandler:
    def __init__(self, parent=None):
        self.parent = parent
        self.error_logger = ErrorLogger()
        
    def show_error(self, error, context=None):
        error_info = self.error_logger.log_error(error, context)
        messagebox.showerror(
            parent=self.parent.winfo_toplevel() if self.parent else None,
            title=error_info["error_type"],
            message=error_info["message"] + "\n\n" + (error_info["solution"] or "")
        )

class ThemeManager:
    def __init__(self):
        self.light_colors = {
            'bg': '#ffffff',
            'fg': '#000000',
            'select_bg': '#0078D7',
            'select_fg': '#ffffff',
            'frame_bg': '#f0f0f0',
        }
        
        self.dark_colors = {
            'bg': '#2d2d2d',
            'fg': '#ffffff',
            'select_bg': '#0078D7',
            'select_fg': '#ffffff',
            'frame_bg': '#363636',
        }
    
    def apply_theme(self, dark_mode: bool, style: ttk.Style, root: tk.Tk):
        colors = self.dark_colors if dark_mode else self.light_colors
        
        # Configure ttk styles
        style.configure('TFrame', background=colors['bg'])
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('TButton', background=colors['bg'], foreground=colors['fg'])
        style.configure('Treeview', background=colors['bg'], foreground=colors['fg'])
        style.configure('TNotebook', background=colors['bg'])
        style.configure('TNotebook.Tab', background=colors['bg'], foreground=colors['fg'])
        
        self._update_widget_colors(root, colors)
    
    def _update_widget_colors(self, widget, colors):
        try:
            widget.configure(bg=colors['bg'], fg=colors['fg'])
        except tk.TclError:
            pass  # Skip widgets that don't support color configuration
            
        for child in widget.winfo_children():
            self._update_widget_colors(child, colors)

class ErrorLogger:
    """Handles error logging and user-friendly error messages"""
    def __init__(self, log_file="AnaFis.log"):
        self.log_file = log_file
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_error(self, error, context=None, suggest_solution=True):
        """Log error and return user-friendly message with solution"""
        # Log the technical error
        logging.error(f"Error: {str(error)}, Context: {context}")
        
        # Common error patterns and solutions
        solutions = {
            "FileNotFoundError": "Please check if the file exists and you have permission to access it.",
            "ValueError": "Please check your input values and ensure they are in the correct format.",
            "SyntaxError": "There appears to be a syntax error in your equation. Please check the formula.",
            "PermissionError": "You don't have permission to access this file. Try running as administrator.",
        }
        
        error_type = type(error).__name__
        solution = solutions.get(error_type, "Please check your input and try again.")
        
        return {
            "error_type": error_type,
            "message": str(error),
            "solution": solution if suggest_solution else None,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context
        }

    
class DataPreview(tk.Toplevel):
    """Preview window for data files"""
    def __init__(self, parent, filepath):
        super().__init__(parent)
        self.title("Data Preview")
        self.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add preview content
        self.create_preview(main_frame, filepath)

    def create_preview(self, parent, filepath):
        try:
            # Determine file type and load data
            ext = Path(filepath).suffix.lower()
            
            # File info frame
            info_frame = ttk.LabelFrame(parent, text="File Information")
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            file_size = os.path.getsize(filepath)
            modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            ttk.Label(info_frame, text=f"File: {os.path.basename(filepath)}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Size: {file_size/1024:.1f} KB").pack(anchor='w')
            ttk.Label(info_frame, text=f"Modified: {modified_time}").pack(anchor='w')

            # Data preview frame
            preview_frame = ttk.LabelFrame(parent, text="Data Preview")
            preview_frame.pack(fill=tk.BOTH, expand=True)

            # Create Treeview for data
            tree = ttk.Treeview(preview_frame)
            tree.pack(fill=tk.BOTH, expand=True)

            # Add scrollbars
            vsb = ttk.Scrollbar(preview_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(preview_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            vsb.pack(side="right", fill="y")
            hsb.pack(side="bottom", fill="x")

            # Load and display data
            if ext in ['.csv', '.txt']:
                df = pd.read_csv(filepath, nrows=100)  # Preview first 100 rows
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath, nrows=100)
            else:
                raise ValueError("Unsupported file format")

            # Configure treeview columns
            tree["columns"] = list(df.columns)
            tree["show"] = "headings"
            
            for column in df.columns:
                tree.heading(column, text=column)
                tree.column(column, width=100)  # Adjust width as needed

            # Add data to treeview
            for idx, row in df.iterrows():
                tree.insert("", "end", values=list(row))

            # Add statistics frame
            stats_frame = ttk.LabelFrame(parent, text="Basic Statistics")
            stats_frame.pack(fill=tk.X, pady=(10, 0))

            # Display basic statistics for numerical columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if not numeric_cols.empty:
                stats = df[numeric_cols].describe()
                for col in numeric_cols:
                    ttk.Label(stats_frame, 
                            text=f"{col} - Mean: {stats[col]['mean']:.2f}, "
                                 f"Std: {stats[col]['std']:.2f}, "
                                 f"Min: {stats[col]['min']:.2f}, "
                                 f"Max: {stats[col]['max']:.2f}").pack(anchor='w')

        except Exception as e:
            ttk.Label(parent, text=f"Error loading preview: {str(e)}",
                     foreground="red").pack(pady=20)


class EquationValidator:
    """
    Validates mathematical equations and provides real-time feedback.
    """
    def __init__(self):
        self.valid_functions = {
            'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',
            'arcsin', 'arccos', 'arctan', 'sinh', 'cosh', 'tanh'
        }
        self.valid_constants = {'pi', 'e'}
        
    def validate_equation(self, equation: str) -> Tuple[bool, str, List[str]]:
        """
        Validates an equation and returns validation status, error message, and found parameters.
        
        Args:
            equation: The equation string to validate
            
        Returns:
            Tuple containing:
            - Boolean indicating if equation is valid
            - Error message (empty if valid)
            - List of parameters found in the equation
        """
        # Remove whitespace and check if empty
        equation = equation.strip()
        if not equation:
            return False, "Equation cannot be empty", []

        try:
            # Replace '^' with '**' for Python syntax
            equation = equation.replace('^', '**')
            
            # Split if equation contains '='
            if '=' in equation:
                parts = equation.split('=')
                if len(parts) > 2:
                    return False, "Equation can only contain one '=' symbol", []
                equation = parts[1].strip()
            
            # Basic syntax check
            if not self._check_basic_syntax(equation):
                return False, "Invalid equation syntax", []
            
            # Parse with sympy
            try:
                expr = sp.sympify(equation)
            except sp.SympifyError as e:
                return False, f"Invalid mathematical expression: {str(e)}", []
            
            # Get parameters (excluding 'x' which is the independent variable)
            x_sym = sp.Symbol('x')
            parameters = sorted(list(expr.free_symbols - {x_sym}), key=lambda s: s.name)
            
            # Validate parameters
            invalid_params = self._validate_parameters(parameters)
            if invalid_params:
                return False, f"Invalid parameter names: {', '.join(invalid_params)}", []
            
            # Check for undefined functions
            undefined_funcs = self._check_undefined_functions(equation)
            if undefined_funcs:
                return False, f"Undefined functions: {', '.join(undefined_funcs)}", []
            
            return True, "", [str(p) for p in parameters]
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", []
    
    def _check_basic_syntax(self, equation: str) -> bool:
        """
        Performs basic syntax validation.
        """
        # Check matching parentheses
        if equation.count('(') != equation.count(')'):
            return False
        
        # Check for invalid characters
        valid_chars = set('0123456789.+-*/()^x ')
        valid_chars.update(self.valid_functions)
        valid_chars.update(self.valid_constants)
        
        # Allow letters for parameter names
        valid_chars.update('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        if not all(c in valid_chars or c.isspace() for c in equation):
            return False
            
        return True
    
    def _validate_parameters(self, parameters: List[sp.Symbol]) -> List[str]:
        """
        Validates parameter names and returns list of invalid parameters.
        """
        invalid_params = []
        for param in parameters:
            param_str = str(param)
            # Check if parameter name is a reserved word
            if param_str in self.valid_functions or param_str in self.valid_constants:
                invalid_params.append(param_str)
            # Check if parameter name starts with a letter and contains only letters and numbers
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', param_str):
                invalid_params.append(param_str)
        return invalid_params
    
    def _check_undefined_functions(self, equation: str) -> List[str]:
        """
        Checks for undefined functions in the equation.
        """
        # Find all potential function calls (words followed by parentheses)
        potential_funcs = re.findall(r'([a-zA-Z]+)\s*\(', equation)
        undefined_funcs = []
        
        for func in potential_funcs:
            if func not in self.valid_functions:
                undefined_funcs.append(func)
                
        return undefined_funcs

class EquationEntry(ttk.Entry):
    """
    Custom Entry widget with real-time equation validation.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.validator = EquationValidator()
        self.valid = False
        self.parameters = []
        
        # Create tooltip
        self.tooltip = None
        
        # Bind events
        self.bind('<KeyRelease>', self._validate_input)
        self.bind('<Enter>', self._show_tooltip)
        self.bind('<Leave>', self._hide_tooltip)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Valid.TEntry', fieldbackground='white')
        self.style.configure('Invalid.TEntry', fieldbackground='#ffe6e6')
        
    def _validate_input(self, event=None):
        """
        Validates input in real-time and updates UI feedback.
        """
        equation = self.get()
        self.valid, error_msg, self.parameters = self.validator.validate_equation(equation)
        
        # Update visual feedback
        if self.valid:
            self.state(['!invalid'])
            self.configure(style='Valid.TEntry')
            self._update_tooltip("")
        else:
            self.state(['invalid'])
            self.configure(style='Invalid.TEntry')
            self._update_tooltip(error_msg)
            
        # Trigger event for parameter updates
        self.event_generate('<<EquationValidated>>')
        
    def _show_tooltip(self, event=None):
        """
        Shows tooltip with validation message.
        """
        if not self.valid and hasattr(self, '_tooltip_text'):
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(self.tooltip, text=self._tooltip_text,
                            justify='left', background="#ffffe0")
            label.pack()
    
    def _hide_tooltip(self, event=None):
        """
        Hides the tooltip.
        """
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            
    def _update_tooltip(self, message: str):
        """
        Updates tooltip text.
        """
        self._tooltip_text = message

class ProgressTracker:
    def __init__(self, progress_var, status_label, odr_object):
        self.progress_var = progress_var
        self.status_label = status_label
        self.odr = odr_object
        self.last_iter = 0
        
    def update(self):
        current_iter = self.odr.iwork[0]  # Current iteration number
        if current_iter != self.last_iter:
            self.last_iter = current_iter
            self.status_label.config(text=f"Iteration: {current_iter}")
            self.progress_var.set(min(100, current_iter * 10))

class UncertaintyCalculationGUI:
    def __init__(self, parent, error_handler=None):
        self.parent = parent
        self.error_handler = error_handler or ErrorHandler(parent)
        self.var_entries = []
        self.create_interface()

    def create_interface(self):
        main_frame = ttk.Frame(self.parent, padding="10")  # Changed from self.root to self.parent
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Operation mode
        ttk.Label(main_frame, text="Operation Mode:").grid(row=0, column=0, pady=5, sticky="w")
        self.mode_var = tk.StringVar(value="calculate")
        ttk.Radiobutton(main_frame, text="Calculate value and uncertainty", variable=self.mode_var, 
                    value="calculate", command=self.update_interface).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(main_frame, text="Generate uncertainty formula", variable=self.mode_var,
                    value="generate", command=self.update_interface).grid(row=2, column=0, sticky="w")

        # Variables input frame
        self.var_frame = ttk.LabelFrame(main_frame, text="Variables", padding="5")
        self.var_frame.grid(row=3, column=0, pady=10, sticky="ew")

        # Number of variables (only for calculate mode)
        self.num_var_frame = ttk.Frame(self.var_frame)
        self.num_var_frame.grid(row=0, column=0, sticky="w")
        ttk.Label(self.num_var_frame, text="Number of variables:").grid(row=0, column=0, sticky="w")
        self.num_var = ttk.Entry(self.num_var_frame, width=5)
        self.num_var.grid(row=0, column=1, padx=2)
        ttk.Button(self.num_var_frame, text="Create fields", 
                command=self.create_variable_fields).grid(row=0, column=2, padx=2)

        # Frame for variable fields
        self.fields_frame = ttk.Frame(self.var_frame)
        self.fields_frame.grid(row=1, column=0, sticky="ew")

        # Formula
        ttk.Label(main_frame, text="Formula:").grid(row=4, column=0, pady=5, sticky="w")
        self.formula_entry = ttk.Entry(main_frame, width=40)
        self.formula_entry.grid(row=5, column=0, pady=5, sticky="ew")

        # Calculate/generate button
        self.calculate_button = ttk.Button(main_frame, text="Calculate", 
                                    command=self.calculate_or_generate)
        self.calculate_button.grid(row=6, column=0, pady=10)

        # Results area
        ttk.Label(main_frame, text="Results:").grid(row=7, column=0, pady=5, sticky="w")
        self.results_text = ScrolledText(
            main_frame, 
            height=12, 
            width=50,
            font=('Courier New', 10)
        )
        self.results_text.grid(row=8, column=0, pady=5, sticky="ew")

        # Copy formula and display LaTeX buttons (initially hidden)
        self.copy_formula_button = ttk.Button(main_frame, text="Copy Formula", 
            command=self.copy_formula)
        self.display_latex_button = ttk.Button(main_frame, text="Display LaTeX", 
            command=lambda: self.display_formula_latex(getattr(self, 'formula_latex', r'')))

        self.update_interface()
        self.results_text.delete(1.0, tk.END)

    def copy_formula(self):
        self.parent.clipboard_clear()  # Use parent ao invés de root
        self.parent.clipboard_append(self.results_text.get(1.0, tk.END))

    def update_interface(self):
        if self.mode_var.get() == "calculate":
            self.num_var_frame.grid()
            self.calculate_button.configure(text="Calculate")
            for widget in self.fields_frame.winfo_children():
                widget.destroy()
            # Hide extra buttons
            self.copy_formula_button.grid_remove()
            self.display_latex_button.grid_remove()
        else:
            self.num_var_frame.grid_remove()
            for widget in self.fields_frame.winfo_children():
                widget.destroy()
            self.calculate_button.configure(text="Generate Formula")
            # For generate mode, only one field for variable list
            ttk.Label(self.fields_frame, text="Variables (comma separated):").grid(row=0, column=0)
            self.vars_entry = ttk.Entry(self.fields_frame, width=30)
            self.vars_entry.grid(row=0, column=1)
            # Show extra buttons below results_text
            self.copy_formula_button.grid(row=9, column=0, pady=5)
            self.display_latex_button.grid(row=10, column=0, pady=5)

    def create_variable_fields(self):
        try:
            num = int(self.num_var.get())
            # Clear existing fields
            for widget in self.fields_frame.winfo_children():
                widget.destroy()
            # Create new fields
            self.var_entries = []
            for i in range(num):
                frame = ttk.Frame(self.fields_frame)
                frame.grid(row=i, column=0, pady=2)
                ttk.Label(frame, text=f"Variable {i+1}:").grid(row=0, column=0)
                name = ttk.Entry(frame, width=5)
                name.grid(row=0, column=1)
                ttk.Label(frame, text="Value:").grid(row=0, column=2)
                value = ttk.Entry(frame, width=10)
                value.grid(row=0, column=3)
                ttk.Label(frame, text="Uncertainty:").grid(row=0, column=4)
                uncertainty = ttk.Entry(frame, width=10)
                uncertainty.grid(row=0, column=5)
                self.var_entries.append((name, value, uncertainty))
        except ValueError:
            self.error_handler.show_error(e, "Context description")

    def calculate_or_generate(self):
        if self.mode_var.get() == "calculate":
            self.calculate_uncertainty()
        else:
            self.generate_uncertainty_formula()

    def calculate_uncertainty(self):
        if not hasattr(self, 'var_entries') or not self.var_entries:
            messagebox.showerror(parent=self.parent.winfo_toplevel(), title="Error", message="Error message")
            return

        try:
            # Collect variables
            variables = {}
            for name_entry, value_entry, uncertainty_entry in self.var_entries:
                name = name_entry.get()
                value = float(value_entry.get())
                uncertainty = float(uncertainty_entry.get())
                variables[name] = (value, uncertainty)
            formula = self.formula_entry.get()
            # Replace sin for users who type in Portuguese
            formula = formula.replace("sen", "sin")
            # Calculate value
            final_value = eval(formula, {"sin": math.sin, "cos": math.cos, "tan": math.tan,
                                     "exp": math.exp, "log": math.log, "sqrt": math.sqrt, "pi": math.pi},
                           {k: value for k, (value, _) in variables.items()})
            # Calculate uncertainty
            total_uncertainty = 0
            expr = sp.sympify(formula)
            for var, (val, sigma) in variables.items():
                derivative = sp.diff(expr, sp.Symbol(var))
                derivative_num = derivative.subs({sp.Symbol(k): value for k, (value, _) in variables.items()})
                derivative_num = float(derivative_num.evalf())
                total_uncertainty += (derivative_num * sigma) ** 2
            total_uncertainty = math.sqrt(total_uncertainty)
            # Show results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "=== Results ===\n")
            self.results_text.insert(tk.END, f"Calculated value: {final_value:.6f}\n")
            self.results_text.insert(tk.END, f"Total uncertainty: ±{total_uncertainty:.6f}\n")
            self.results_text.insert(tk.END, f"Final result: ({final_value:.6f} ± {total_uncertainty:.6f})")
        except Exception as e:
            self.error_handler.show_error(e, "Context description")

    def generate_uncertainty_formula(self):
        try:
            variables = self.vars_entry.get().split(',')
            formula = self.formula_entry.get()
            formula = formula.replace("sen", "sin")   # allows Portuguese "sen" usage
            symbols = {var.strip(): sp.Symbol(var.strip()) for var in variables}
            expr = sp.sympify(formula, locals=symbols)
            terms = []
            for var in variables:
                var = var.strip()
                derivative = sp.diff(expr, symbols[var])
                terms.append(f"(\\sigma_{{{var}}} \\cdot {sp.latex(derivative)})^2")
            formula_incerteza = "\\sigma_{\\text{total}} = \\sqrt{" + " + ".join(terms) + "}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "=== Uncertainty Formula (LaTeX) ===\n\n")
            self.results_text.insert(tk.END, "Copy the code below for LaTeX:\n\n")
            self.results_text.insert(tk.END, f"{formula_incerteza}\n\n")
            self.results_text.insert(tk.END, "Click 'Display LaTeX' to view the rendered formula.\n")
            self.formula_latex = formula_incerteza  # Store for visualization
        except Exception as e:
            self.error_handler.show_error(e, "Context description")

    def display_formula_latex(self, formula_latex):
        if not formula_latex or formula_latex.strip() == "":
            messagebox.showinfo("Attention", "Generate the formula first!")
            return
        window = Toplevel(self.parent)
        window.title("Rendered Formula (LaTeX)")
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula_latex}$", fontsize=18, ha='center', va='center')
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

class CurveFittingGUI:
    def __init__(self, parent):
        self.parent = parent
        self.error_handler = ErrorHandler(parent) 

        
        # Configure main layout with weights
        parent.columnconfigure(0, weight=2)  # Parameters column
        parent.columnconfigure(1, weight=3)  # Graph column
        parent.rowconfigure(0, weight=1)
        
        # Variables to store data
        self.parameters = []
        # Create figure before creating panels
        self.fig = plt.figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        
        # Create panels
        self.create_parameters_panel()
        self.create_graph_panel()

        style = ttk.Style()
        style.configure("Accent.TButton", font=('Helvetica', 10, 'bold'))

    def update_scales(self):
        try:
            self.ax.set_xscale('log' if self.x_scale.get() == "Log" else 'linear')
            self.ax.set_yscale('log' if self.y_scale.get() == "Log" else 'linear')
            self.canvas.draw()
        except Exception as e:
            self.error_handler.show_error(e, "Error updating scales")
        
    def create_parameters_panel(self):
        # Left frame for parameters with padding and border
        left_frame = ttk.Frame(self.parent, padding="10")  # Changed from self.root to self.parent
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        # Input data frame
        data_frame = ttk.LabelFrame(left_frame, text="Input Data", padding="5")
        data_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,10))
        
        # Data file
        ttk.Label(data_frame, text="Data File:").grid(row=0, column=0, sticky="w", pady=5)
        self.file_entry = ttk.Entry(data_frame, width=40)
        self.file_entry.grid(row=1, column=0, sticky="ew", padx=5)
        ttk.Button(data_frame, text="Browse", command=self.select_file).grid(row=1, column=1)
        
        # Equation and fitting parameters
        fitting_frame = ttk.LabelFrame(left_frame, text="Fitting Parameters", padding="5")
        fitting_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,10))
        
        ttk.Label(fitting_frame, text="Equation:").grid(row=0, column=0, sticky="w", pady=5)
        self.equation_entry = EquationEntry(fitting_frame, width=40)  # Use custom widget
        self.equation_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
    
        # Bind to equation validation event
        self.equation_entry.bind('<<EquationValidated>>', self._on_equation_validated)
        # Numerical settings frame
        config_frame = ttk.Frame(fitting_frame)
        config_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(config_frame, text="Max iterations:").grid(row=0, column=0, sticky="w")
        self.max_iter_entry = ttk.Entry(config_frame, width=8)
        self.max_iter_entry.insert(0, "1000")
        self.max_iter_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Fitting points:").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.num_points_entry = ttk.Entry(config_frame, width=8)
        self.num_points_entry.insert(0, "1000")
        self.num_points_entry.grid(row=0, column=3, padx=5)
        
        # Graph settings frame
        graph_frame = ttk.LabelFrame(left_frame, text="Graph Settings", padding="5")
        graph_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0,10))
        
        ttk.Label(graph_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = ttk.Entry(graph_frame, width=40)
        self.title_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Scales
        scale_frame = ttk.Frame(graph_frame)
        scale_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(scale_frame, text="X Scale:").grid(row=0, column=0, padx=5)
        self.x_scale = ttk.Combobox(scale_frame, values=["Linear", "Log"], state="readonly", width=8)
        self.x_scale.set("Linear")
        self.x_scale.grid(row=0, column=1, padx=5)
        
        ttk.Label(scale_frame, text="Y Scale:").grid(row=0, column=2, padx=(10,5))
        self.y_scale = ttk.Combobox(scale_frame, values=["Linear", "Log"], state="readonly", width=8)
        self.y_scale.set("Linear")
        self.y_scale.grid(row=0, column=3, padx=5)
        
        # Initial estimates frame
        self.estimates_frame = ttk.LabelFrame(left_frame, text="Initial Estimates", padding="5")
        self.estimates_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,10))
        
        # Progress frame
        progress_frame = ttk.LabelFrame(left_frame, text="Progress", padding="5")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0,10))
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.grid(row=1, column=0, sticky="w", padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(left_frame, text="Results", padding="5")
        results_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0,10))
        
        self.results_text = ScrolledText(results_frame, height=8, width=40)
        self.results_text.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Action buttons
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0,5))
        
        ttk.Button(
            buttons_frame, 
            text="Perform Fitting",
            style="Accent.TButton",
            command=self.perform_fitting
        ).grid(row=0, column=0, pady=5, padx=5, sticky="ew")
        
        ttk.Button(
            buttons_frame,
            text="Save Graph",
            command=self.save_graph
        ).grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        
        # Configure column weights
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        # Bindings
        self.equation_entry.bind("<FocusOut>", lambda e: self.update_estimates_frame())
        self.x_scale.bind('<<ComboboxSelected>>', lambda e: self.update_scales())
        self.y_scale.bind('<<ComboboxSelected>>', lambda e: self.update_scales())

    def _on_equation_validated(self, event=None):
        """
        Handler for equation validation events.
        """
        if self.equation_entry.valid:
            # Update parameters only if equation is valid
            self.parameters = self.equation_entry.parameters
            self.update_estimates_frame()

    def save_graph(self):
        try:
            # Open dialog to choose location and filename
            filetypes = [
                ('PNG', '*.png'),
                ('PDF', '*.pdf'),
                ('SVG', '*.svg'),
                ('JPEG', '*.jpg')
            ]
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=filetypes,
                title="Save Graph As"
            )
            
            if filename:
                # Adjust layout before saving
                self.fig.tight_layout()
                
                # Save the graph
                self.fig.savefig(
                    filename, 
                    dpi=300, 
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                
                messagebox.showinfo(
                    "Success",
                    f"Graph saved successfully at:\n{filename}"
                )
                
        except Exception as e:
            self.error_handler.show_error(e, "Error saving graph")

    def create_graph_panel(self):
        # Right frame for graph with padding
        right_frame = ttk.Frame(self.parent, padding="10")  # Changed from self.root to self.parent
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Frame for graph
        graph_frame = ttk.LabelFrame(right_frame, text="Fitting Graph", padding="5")
        graph_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure figure size
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        
        # Canvas for graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure column weight
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select data file",
            filetypes=[("Text or CSV files", "*.txt *.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            
    def update_estimates_frame(self):
        # Clear current frame
        for widget in self.estimates_frame.winfo_children():
            widget.destroy()
            
        # Extract parameters from equation
        try:
            equation = self.equation_entry.get().replace('^', '**')
            if '=' in equation:
                equation = equation.split('=')[1].strip()
                
            x_sym = sp.Symbol('x')
            expr = sp.sympify(equation)
            self.parameters = sorted(list(expr.free_symbols - {x_sym}), key=lambda s: s.name)
            
            # Create input fields for each parameter
            for i, param in enumerate(self.parameters):
                ttk.Label(self.estimates_frame, text=f"{param}:").grid(row=i, column=0, padx=5, pady=2)
                entry = ttk.Entry(self.estimates_frame, width=10)
                entry.insert(0, "1.0")
                entry.grid(row=i, column=1, padx=5, pady=2)
                setattr(self, f"estimate_{param}", entry)
                
        except Exception as e:
            messagebox.showerror(parent=self.parent.winfo_toplevel(), title="Error", message="Error message")
            
    def read_file(self, filename):
        if not os.path.isfile(filename):
            messagebox.showerror(parent=self.parent.winfo_toplevel(), title="Error", message="Error message")
            raise FileNotFoundError(f"The file '{filename}' was not found.")
        try:
            # Detect separator type by file extension
            _, ext = os.path.splitext(filename)
            if ext.lower() == ".csv":
                delimiter = ','
            else:
                delimiter = '\t'

            with open(filename, 'r') as f:
                header = f.readline()
                lines = f.readlines()
            if len(lines) == 0:
                messagebox.showerror("Error reading file", "The file is empty or contains only header.")
                raise ValueError("The file is empty or contains only header.")

            # Check number of columns generically (works for both formats)
            for i, line in enumerate(lines):
                parts = line.strip().split(delimiter)
                if len(parts) != 4:
                    messagebox.showerror("Error reading file",
                        f"The file must have 4 columns separated by '{delimiter}' (line {i+2}).")
                    raise ValueError(f"The file must have 4 columns separated by '{delimiter}' (line {i+2}).")
            # Load data using numpy
            data = np.genfromtxt(filename, delimiter=delimiter, skip_header=1, dtype=str)
            data = np.char.replace(data, ',', '.')
            x = data[:, 0].astype(float)
            sigma_x = data[:, 1].astype(float)
            y = data[:, 2].astype(float)
            sigma_y = data[:, 3].astype(float)
            return x, sigma_x, y, sigma_y
        except Exception as e:
            messagebox.showerror(parent=self.parent.winfo_toplevel(), title="Error", message="Error message")
            raise
    
    def create_model(self, equation, parameters):
        x = sp.Symbol('x')
        expr = sp.sympify(equation)
        
        derivatives = [sp.diff(expr, p) for p in parameters]
        
        numerical_model = sp.lambdify((parameters, x), expr, 'numpy')
        numerical_derivatives = [sp.lambdify((parameters, x), d, 'numpy') for d in derivatives]
        
        return numerical_model, numerical_derivatives
    
    def perform_fitting(self):
        try:
            num_points = int(self.num_points_entry.get())
            if num_points <= 0:
                raise ValueError("Number of points must be positive")
        except ValueError as e:
            messagebox.showerror(parent=self.parent.winfo_toplevel(), title="Error", message="Error message")
            return
        try:
            # Reset progress and status
            self.progress_var.set(0)
            self.status_label.config(text="Starting fitting...")
            self.parent.update()

            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Update estimates if needed
            if not self.parameters:
                self.update_estimates_frame()
                
            # Get field values
            path = self.file_entry.get()
            equation = self.equation_entry.get().replace('^', '**')
            if '=' in equation:
                equation = equation.split('=')[1].strip()
            max_iter = int(self.max_iter_entry.get())
            
            # Get initial estimates
            guess = []
            for param in self.parameters:
                entry = getattr(self, f"estimate_{param}")
                guess.append(float(entry.get()))
                
            # Load data
            self.x, self.sigma_x, self.y, self.sigma_y = self.read_file(path)
            with open(path, 'r') as f:
                self.header = f.readline().strip().split('\t')
                
            # Create model
            self.model, derivatives = self.create_model(equation, self.parameters)
            odr_model = Model(ODRModel(self.model, derivatives))
            self.equation = equation

            # Execute ODR
            data = RealData(self.x, self.y, sx=self.sigma_x, sy=self.sigma_y)
            self.odr = ODR(data, odr_model, beta0=guess, maxit=max_iter)
            
            def run_odr():
                try:
                    result = self.odr.run()
                    self.parent.after(0, lambda: self.show_results(result))
                    self.parent.after(0, lambda: self.status_label.config(text="Fitting completed!"))
                except Exception as e:
                    self.parent.after(0, lambda: messagebox.showerror("Error", f"Error during fitting: {str(e)}"))
                    self.parent.after(0, lambda: self.status_label.config(text="Error in fitting!"))

            def update_progress():
                if hasattr(self, 'odr'):
                    try:
                        current_iter = self.odr.iwork[0]
                        self.progress_var.set(min(100, current_iter * 10))
                        self.status_label.config(text=f"Iteration: {current_iter}")
                        if current_iter < max_iter:
                            self.root.after(100, update_progress)
                    except:
                        pass

            # Start progress updates
            self.root.after(100, update_progress)
            
            # Start ODR in separate thread
            threading.Thread(target=run_odr, daemon=True).start()

        except Exception as e:
            self.error_handler.show_error(e, "Error during fitting")
    
   
    def show_results(self, result):
        try:
            # Limpe a figura antes de plotar novos dados
            self.ax.clear()
            
            # Calcule os resultados
            y_pred = self.model(result.beta, self.x)
            chi2_total = np.sum(((self.y - y_pred) / self.sigma_y) ** 2)
            r2 = 1 - np.sum((self.y - y_pred) ** 2) / np.sum((self.y - np.mean(self.y)) ** 2)
            
            # Atualize o texto dos resultados
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "=== Results ===\n")
            for p, v, e in zip(self.parameters, result.beta, result.sd_beta):
                self.results_text.insert(tk.END, f"{p} = {v:.6f} ± {e:.6f}\n")
            self.results_text.insert(tk.END, f"\nTotal Chi²: {chi2_total:.2f}\n")
            self.results_text.insert(tk.END, f"Reduced Chi²: {result.res_var:.2f}\n")
            self.results_text.insert(tk.END, f"R²: {r2:.4f}\n")
            
            # Plote os dados
            self.plot_results(result, y_pred)
            
        except Exception as e:
            self.error_handler.show_error(e, "Error showing results")

    def plot_results(self, result, y_pred):
        try:
            self.ax.errorbar(self.x, self.y, xerr=self.sigma_x, yerr=self.sigma_y, 
                            fmt='o', label='Data')
            
            num_points = int(self.num_points_entry.get())
            x_fit = np.linspace(min(self.x), max(self.x), num_points)
            self.ax.plot(x_fit, self.model(result.beta, x_fit), 'r-', label='Fit')
            
            # Configure o gráfico
            if self.title_entry.get():
                self.ax.set_title(self.title_entry.get())
            self.ax.set_xlabel(self.header[0])
            self.ax.set_ylabel(self.header[2])
            self.ax.legend()
            self.ax.grid(True)
            
            # Add text box with information
            info_text = f"Equation: y = {self.equation}\n"
            info_text += '\n'.join([f"{p} = {v:.6f} ± {e:.6f}" for p, v, e in 
                                zip(self.parameters, result.beta, result.sd_beta)])
            info_text += f"\nTotal Chi²: {chi2_total:.2f}\nReduced Chi²: {result.res_var:.2f}\nR²: {r2:.4f}"
            
            self.ax.text(
                0.98, 0.02,
                info_text,
                transform=self.ax.transAxes,
                fontsize=7,
                bbox=dict(facecolor='white', alpha=0.5),
                ha='right',
                va='bottom'
            )
            
            self.add_info_box(result)
        
            # Atualize as escalas e o canvas
            self.update_scales()
            self.canvas.draw()
        
        except Exception as e:
            self.error_handler.show_error(e, "Error plotting results")
            
class ODRModel:
    def __init__(self, function, derivatives):
        self.function = function
        self.derivatives = derivatives
        
    def __call__(self, parameters, x):
        return self.function(parameters, x)

    def fjb(self, parameters, x):
        """
        Returns the derivatives with respect to parameters.
        """
        return [d(parameters, x) for d in self.derivatives]

    def fdb(self, parameters, x):
        """
        Returns the derivative with respect to the independent variable.
        """
        return np.zeros_like(x)

class ModernGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.title("Physics Data Analysis")
        self.geometry("1200x800")
        
        # Initialize managers
        self.error_handler = ErrorHandler(self)
        self.theme_manager = ThemeManager()
        
        # Initialize variables
        self.dark_mode = tk.BooleanVar(value=False)
        self.recent_files = []
        
        # Create the UI
        self.create_style()
        self.create_main_frame()
        self.create_menu()
        self.create_tabs()
        
        # Apply initial theme
        self.theme_manager.apply_theme(False, self.style, self)
    
    def create_style(self):
        """Create and initialize style"""
        self.style = ttk.Style()
        
    def create_main_frame(self):
        """Create the main application frame"""
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Analysis", command=self.new_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(
            label="Dark Mode", 
            variable=self.dark_mode,
            command=lambda: self.theme_manager.apply_theme(
                self.dark_mode.get(), 
                self.style, 
                self
            )
        )

    def create_tabs(self):
        """Create and initialize the application tabs"""
        # Create frames for tabs
        self.curve_fitting_frame = ttk.Frame(self.notebook)
        self.uncertainty_frame = ttk.Frame(self.notebook)
        
        # Configure frame grid
        self.curve_fitting_frame.columnconfigure(0, weight=1)
        self.curve_fitting_frame.rowconfigure(0, weight=1)
        self.uncertainty_frame.columnconfigure(0, weight=1)
        self.uncertainty_frame.rowconfigure(0, weight=1)
        
        # Add frames to notebook
        self.notebook.add(self.curve_fitting_frame, text="Curve Fitting")
        self.notebook.add(self.uncertainty_frame, text="Uncertainty Calculation")
        
        # Initialize tab content
        self.init_curve_fitting()
        self.init_uncertainty_calc()

    def init_curve_fitting(self):
        """Initialize the curve fitting tab"""
        self.curve_fitting = CurveFittingGUI(self.curve_fitting_frame)
    
    def init_uncertainty_calc(self):
        """Initialize the uncertainty calculation tab"""
        self.uncertainty_calc = UncertaintyCalculationGUI(
            self.uncertainty_frame, 
            self.error_handler
        )
    
    def new_analysis(self):
        selected = self.notebook.select()
        tab_id = self.notebook.index(selected)
        
        if tab_id == 0:  # Curve Fitting tab
            self.init_curve_fitting()
        else:  # Uncertainty Calculation tab
            self.init_uncertainty_calc()

    def open_file(self, filepath=None):
        """Open a file with preview"""
        try:
            if filepath is None:
                filepath = filedialog.askopenfilename(
                    filetypes=[
                        ("Data files", "*.csv;*.txt;*.xlsx;*.xls"),
                        ("All files", "*.*")
                    ]
                )
                
            if filepath:
                # Show preview
                preview = DataPreview(self, filepath)
                preview.transient(self)
                preview.grab_set()
                self.wait_window(preview)
                
                # Add to recent files
                self.recent_files.add_file(filepath)
                self.update_recent_menu()
                
        except Exception as e:
            self.show_error(e, f"Opening file: {filepath}")

if __name__ == "__main__":
    app = ModernGUI()
    app.mainloop()