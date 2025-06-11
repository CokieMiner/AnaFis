"""GUI module for uncertainty calculations"""
from __future__ import annotations
from typing import Tuple, Dict, List, Optional
import tkinter as tk
from tkinter import ttk, Toplevel
from tkinter.messagebox import showerror, showinfo # type: ignore
from tkinter.scrolledtext import ScrolledText
import math
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from app_files.utils.constants import TRANSLATIONS

# Constants
FONT_FAMILY = 'Courier New'
FONT_SIZE = 10
ENTRY_WIDTH = {'small': 5, 'medium': 10, 'large': 30, 'formula': 40}


class CalculoIncertezasFrame:
    """Frame-based GUI class for uncertainty calculations"""

    def __init__(self, parent: tk.Widget, language: str = 'pt') -> None:
        """Initialize the frame        
        Args:
            parent: Parent widget (typically a tab)
            language: Interface language (default: 'pt')
        """
        self.parent = parent
        self.language = language
        
        # Initialize all attributes
        self.vars_entry: Optional[ttk.Entry] = None
        self.var_entries: List[Tuple[ttk.Entry, ttk.Entry, ttk.Entry]] = []
        self.formula_latex: str = ""
        self.modo_var = tk.StringVar(value="calcular")
        self.num_var: ttk.Entry
        self.formula_entry: ttk.Entry
        self.botao_calcular: ttk.Button
        self.resultados_text: ScrolledText
        self.latex_frame: ttk.Frame
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize the UI
        self.setup_ui()

    def on_tab_activated(self) -> None:
        """Called when this tab becomes active"""
        self.update_results()

    def cleanup(self) -> None:
        """Clean up resources when tab is closed or application exits"""
        if hasattr(self, 'latex_frame'):
            for widget in self.latex_frame.winfo_children():
                widget.destroy()

    def update_results(self) -> None:
        """Update calculation results"""
        if not self.formula_entry.get():
            return

    def setup_ui(self) -> None:
        """Set up the user interface components"""
        self.main_frame.columnconfigure(0, weight=1)
        
        # Operation mode
        operation_mode_label = ttk.Label(
            self.main_frame,
            text=TRANSLATIONS[self.language]['operation_mode']
        )
        operation_mode_label.grid(row=0, column=0, pady=5, sticky="w")
        
        calc_radio = ttk.Radiobutton(
            self.main_frame,
            text=TRANSLATIONS[self.language]['calc_value_uncertainty'],
            variable=self.modo_var,
            value="calcular",
            command=self.atualizar_interface
        )
        calc_radio.grid(row=1, column=0, sticky="w")
        
        generate_radio = ttk.Radiobutton(
            self.main_frame,
            text=TRANSLATIONS[self.language]['generate_uncertainty_formula'],
            variable=self.modo_var,
            value="gerar",
            command=self.atualizar_interface
        )
        generate_radio.grid(row=2, column=0, sticky="w")
        
        # Variables frame
        var_frame_text = TRANSLATIONS[self.language]['variables']
        self.var_frame = ttk.LabelFrame(
            self.main_frame,
            text=var_frame_text,
            padding="5"
        )
        self.var_frame.grid(row=3, column=0, pady=10, sticky="ew")

        # Number of variables
        self.num_var_frame = ttk.Frame(self.var_frame)
        self.num_var_frame.grid(row=0, column=0, sticky="w")
        
        num_vars_label = ttk.Label(
            self.num_var_frame,
            text=TRANSLATIONS[self.language]['number_of_variables']
        )
        num_vars_label.grid(row=0, column=0, sticky="w")
        
        self.num_var = ttk.Entry(self.num_var_frame, width=ENTRY_WIDTH['small'])
        self.num_var.grid(row=0, column=1, padx=2)
        
        create_fields_btn = ttk.Button(
            self.num_var_frame,
            text=TRANSLATIONS[self.language]['create_fields'],
            command=self.criar_campos_variaveis
        )
        create_fields_btn.grid(row=0, column=2, padx=2)

        # Variable fields frame
        self.campos_frame = ttk.Frame(self.var_frame)
        self.campos_frame.grid(row=1, column=0, sticky="ew")
        self.campos_frame.grid_columnconfigure(0, weight=1) 
        # Ensure the column within campos_frame expands

        # Formula
        formula_label = ttk.Label(
            self.main_frame,
            text=TRANSLATIONS[self.language]['formula']
        )
        formula_label.grid(row=4, column=0, pady=5, sticky="w")
        
        self.formula_entry = ttk.Entry(
            self.main_frame,
            width=ENTRY_WIDTH['formula']
        )
        self.formula_entry.grid(row=5, column=0, pady=5, sticky="ew")

        # Calculate/generate button
        calc_btn_text = TRANSLATIONS[self.language]['calculate']
        self.botao_calcular = ttk.Button(
            self.main_frame,
            text=calc_btn_text,
            command=self.calcular_ou_gerar
        )
        self.botao_calcular.grid(row=6, column=0, pady=10)
        
        # Results area
        results_label = ttk.Label(
            self.main_frame,
            text=TRANSLATIONS[self.language]['results']
        )
        results_label.grid(row=7, column=0, pady=5, sticky="w")
        
        self.resultados_text = ScrolledText(
            self.main_frame,
            height=12,
            width=50,
            font=(FONT_FAMILY, FONT_SIZE)
        )
        self.resultados_text.grid(row=8, column=0, pady=5, sticky="ew")

        # LaTeX frame
        self.latex_frame = ttk.Frame(self.main_frame)
        self.latex_frame.grid(row=9, column=0, pady=5, sticky="ew")
        
        self.atualizar_interface()
        self.resultados_text.delete(1.0, tk.END)

    def atualizar_interface(self) -> None:
        """Update interface based on selected operation mode"""
        mode = self.modo_var.get()
        
        if mode == "calcular":
            self.num_var_frame.grid()
            self.botao_calcular.configure(
                text=TRANSLATIONS[self.language]['calculate']
            )
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
        else:
            self.num_var_frame.grid_remove()
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
                
            self.botao_calcular.configure(
                text=TRANSLATIONS[self.language]['generate_formula']
            )
            
            # For generate mode - single variable list field
            vars_list_text = TRANSLATIONS[self.language]['variables_list']
            vars_label = ttk.Label(self.campos_frame, text=vars_list_text)
            vars_label.grid(row=0, column=0)
            
            self.vars_entry = ttk.Entry(
                self.campos_frame,
                width=ENTRY_WIDTH['large']
            )
            self.vars_entry.grid(row=0, column=1)

    def criar_campos_variaveis(self) -> None:
        """Create input fields for variables based on the number specified"""
        try:
            num = int(self.num_var.get())
            # Clear existing fields
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
                
            self.var_entries = [] # Reset var_entries list
            
            # Column headers
            header_frame = ttk.Frame(self.campos_frame)
            header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
            
            # Configure column weights for header_frame
            header_frame.grid_columnconfigure(0, weight=0) # Spacer column
            header_frame.grid_columnconfigure(1, weight=1) # Variable header
            header_frame.grid_columnconfigure(2, weight=1) # Value header
            header_frame.grid_columnconfigure(3, weight=1) # Uncertainty header
            
            ttk.Label(header_frame, text="").grid(row=0, column=0, padx=2) # Spacer
            
            header_labels_text = [
                TRANSLATIONS[self.language]['variable'],
                TRANSLATIONS[self.language]['value'],
                TRANSLATIONS[self.language]['uncertainty']
            ]
            for col, text in enumerate(header_labels_text):
                ttk.Label(header_frame, text=text).grid(row=0, column=col + 1, padx=2, sticky="ew") 
            
            for i in range(num):
                frame = ttk.Frame(self.campos_frame)
                frame.grid(row=i+1, column=0, pady=2, sticky="ew")

                # Configure column weights for individual variable row frame
                frame.grid_columnconfigure(0, weight=0) # Row number column
                frame.grid_columnconfigure(1, weight=1) # Name entry
                frame.grid_columnconfigure(2, weight=1) # Value entry
                frame.grid_columnconfigure(3, weight=1) # Uncertainty entry
                
                ttk.Label(frame, text=f"{i+1}:").grid(row=0, column=0, padx=2, sticky='w')
                
                nome = ttk.Entry(frame, width=ENTRY_WIDTH['medium'])
                nome.grid(row=0, column=1, padx=2, sticky="ew")
                
                valor = ttk.Entry(frame, width=ENTRY_WIDTH['medium'])
                valor.grid(row=0, column=2, padx=2, sticky="ew")
                
                incerteza = ttk.Entry(frame, width=ENTRY_WIDTH['medium'])
                incerteza.grid(row=0, column=3, padx=2, sticky="ew")
                
                self.var_entries.append((nome, valor, incerteza))

        except ValueError:
            error_msg = TRANSLATIONS[self.language]['invalid_vars']
            showerror(title="Error", message=error_msg)

    def calcular_ou_gerar(self) -> None:
        """Route to appropriate calculation or generation method based on mode"""
        if self.modo_var.get() == "calcular":
            self.calcular_incerteza()
        else:
            self.gerar_formula_incerteza()

    def calcular_incerteza(self) -> None:
        """Calculate uncertainty for given variables and formula"""
        if not self.var_entries:
            error_msg = TRANSLATIONS[self.language]['create_fields']
            showerror(title="Error", message=error_msg)
            return

        try:
            # Collect variables
            variaveis: Dict[str, Tuple[float, float]] = {}
            for nome_entry, valor_entry, incerteza_entry in self.var_entries:
                nome = nome_entry.get()
                valor = float(valor_entry.get())
                incerteza = float(incerteza_entry.get())
                variaveis[nome] = (valor, incerteza)

            formula = self.formula_entry.get().replace("sen", "sin")

            # Create symbol mapping for sympy
            variables_dict_sympy = {sp.Symbol(k): v[0] for k, v in variaveis.items()}
            
            # Calculate final value using sympy
            expr: sp.Expr = sp.sympify(formula) # type: ignore
            valor_final = float(expr.subs(variables_dict_sympy).evalf()) # type: ignore
            
            # Calculate uncertainty
            incerteza_total = self._calcular_incerteza_total(formula, variaveis)
            
            # Show results
            self._mostrar_resultados(valor_final, incerteza_total)

        except (ValueError, TypeError, sp.SympifyError) as e: # Simplified exceptions
            showerror(title="Error", message=str(e))

    def _calcular_incerteza_total(
        self, 
        formula: str,
        variaveis: Dict[str, Tuple[float, float]]
    ) -> float:
        """Calculate total uncertainty using partial derivatives"""
        incerteza_total = 0.0
        expr: sp.Expr = sp.sympify(formula) # type: ignore
        symbols_map = {sp.Symbol(k): v[0] for k, v in variaveis.items()}
        
        for var, (_, sigma) in variaveis.items():
            symbol = sp.Symbol(var)
            derivada: sp.Expr = sp.diff(expr, symbol) # type: ignore
            derivada_num = derivada.subs(symbols_map) # type: ignore
            derivada_num_val = float(derivada_num.evalf()) # type: ignore
            incerteza_total += (derivada_num_val * sigma) ** 2
            
        return math.sqrt(incerteza_total)

    def _mostrar_resultados(self, valor: float, incerteza: float) -> None:
        """Display calculation results in the text area"""
        self.resultados_text.delete(1.0, tk.END)
        trans = TRANSLATIONS[self.language]
        self.resultados_text.insert(tk.END, f"{trans['result_header']}\n")
        self.resultados_text.insert(tk.END, f"{trans['calculated_value']} {valor:.6f}\n")
        self.resultados_text.insert(tk.END, f"{trans['total_uncertainty']} ±{incerteza:.6f}\n")
        self.resultados_text.insert(tk.END, 
            f"{trans['final_result']} ({valor:.6f} ± {incerteza:.6f})"
        )

        # Clear LaTeX display
        self._clear_latex_display()

    def _clear_latex_display(self) -> None:
        """Clear any LaTeX rendering from the interface"""
        for widget in self.latex_frame.winfo_children():
            widget.destroy()

    def gerar_formula_incerteza(self) -> None:
        """Generate uncertainty formula for given variables"""
        if self.vars_entry is None:
            return

        try:
            variaveis_str = [v.strip() for v in self.vars_entry.get().split(',')]
            if not all(variaveis_str): # Check for empty variable names
                showerror(title="Input Error", message=TRANSLATIONS[self.language]['empty_variable_name'])
                return

            formula = self.formula_entry.get().replace("sen", "sin")
            if not formula:
                showerror(title="Input Error", message=TRANSLATIONS[self.language]['empty_formula'])
                return
            
            # Create symbol mapping
            simbolos = {var: sp.Symbol(var) for var in variaveis_str}
            expr: sp.Expr = sp.sympify(formula, locals=simbolos) # type: ignore
            
            # Generate uncertainty terms
            termos: List[str] = []
            for var_str in variaveis_str:
                derivada: sp.Expr = sp.diff(expr, simbolos[var_str]) # type: ignore
                latex_term = f"({sp.latex(derivada)} \\\\cdot \\\\delta_{{{var_str}}})^2"
                termos.append(latex_term)

            formula_incerteza = "\\delta_{\\text{total}} = \\sqrt{" + " + ".join(termos) + "}"
            
            # Display results
            self.resultados_text.delete(1.0, tk.END)
            trans = TRANSLATIONS[self.language]
            self.resultados_text.insert(tk.END, f"{trans['uncertainty_formula_header']}\n\n")
            self.resultados_text.insert(tk.END, f"{trans['copy_latex_code']}\n\n")
            self.resultados_text.insert(tk.END, f"{formula_incerteza}\n\n")
            self.formula_latex = formula_incerteza
            
            # Render LaTeX
            self._renderizar_formula_incerteza_na_interface(formula_incerteza)

        except sp.SympifyError as e:
            showerror(title="Formula Error", message=f"{TRANSLATIONS[self.language]['invalid_formula']}: {str(e)}")
        except ValueError as e: # Catch specific errors for better feedback
            showerror(title="Value Error", message=str(e))
        except Exception as e: # Catch all other potential errors
            showerror(title="Error", message=f"{TRANSLATIONS[self.language]['unexpected_error']}: {str(e)}")

    def _renderizar_formula_incerteza_na_interface(self, formula_latex: str) -> None:
        """Render the uncertainty formula using matplotlib"""
        self._clear_latex_display()
        
        fig = Figure(figsize=(7, 2))
        ax: Axes = fig.add_subplot(111) # type: ignore
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula_latex}$", # type: ignore
                fontsize=16, ha='center', va='center')
        fig.tight_layout(pad=0)

        canvas = FigureCanvasTkAgg(fig, master=self.latex_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def exibir_formula_latex(self, formula_latex: str) -> None:
        """Display LaTeX formula in a separate window"""
        if not formula_latex.strip():
            showinfo(title="Notice", message=TRANSLATIONS[self.language]['generate_formula']) # Already covered by line 6 ignore
            return
            
        janela = Toplevel(self.parent)
        janela.title("Rendered Formula (LaTeX)")
        
        fig = Figure(figsize=(7, 2))
        ax: Axes = fig.add_subplot(111) # type: ignore
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula_latex}$", # type: ignore
                fontsize=18, ha='center', va='center')
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

    def switch_language(self, language: str) -> None:
        """Update language for this component"""
        self.language = language
        current_mode = self.modo_var.get()
        current_formula = self.formula_entry.get()
        current_num_vars = self.num_var.get()

        # Clear and rebuild UI
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.setup_ui()

        # Restore state
        self.modo_var.set(current_mode)
        self.formula_entry.insert(0, current_formula)
        self.num_var.insert(0, current_num_vars)
        self.atualizar_interface()