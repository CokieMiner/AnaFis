"""GUI module for uncertainty calculations"""
from __future__ import annotations
from typing import Tuple, Dict
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText
import math
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

from app_files.utils.constants import TRANSLATIONS

# Constants
FONT_FAMILY = 'Courier New'
FONT_SIZE = 10
PADDING = "10"
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
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize the UI
        self.setup_ui()
        
    def on_tab_activated(self):
        """Called when this tab becomes active"""
        # Update any UI elements that need refreshing
        self.update_results()
        
    def cleanup(self):
        """Clean up resources when tab is closed or application exits"""
        # Clean up any resources if needed
        pass
        
    def update_results(self):
        """Update calculation results"""
        if not hasattr(self, 'formula_entry') or not self.formula_entry.get():
            # Skip update if no formula entered
            return
            
    def setup_ui(self) -> None:
        """Set up the user interface components"""
        # Configure column weights for proper expansion
        self.main_frame.columnconfigure(0, weight=1)
        
        # Modo de operação
        ttk.Label(self.main_frame, text=TRANSLATIONS[self.language]['operation_mode']).grid(row=0, column=0, pady=5, sticky="w")
        self.modo_var = tk.StringVar(value="calcular")
        ttk.Radiobutton(self.main_frame, text=TRANSLATIONS[self.language]['calc_value_uncertainty'], 
                    variable=self.modo_var, value="calcular", 
                    command=self.atualizar_interface).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(self.main_frame, text=TRANSLATIONS[self.language]['generate_uncertainty_formula'],
                    variable=self.modo_var, value="gerar",
                    command=self.atualizar_interface).grid(row=2, column=0, sticky="w")

        # Frame para entrada de variáveis
        self.var_frame = ttk.LabelFrame(self.main_frame, text=TRANSLATIONS[self.language]['variables'], padding="5")
        self.var_frame.grid(row=3, column=0, pady=10, sticky="ew")

        # Número de variáveis (apenas para modo calcular)
        self.num_var_frame = ttk.Frame(self.var_frame)
        self.num_var_frame.grid(row=0, column=0, sticky="w")
        ttk.Label(self.num_var_frame, text=TRANSLATIONS[self.language]['number_of_variables']).grid(row=0, column=0, sticky="w")
        self.num_var = ttk.Entry(self.num_var_frame, width=ENTRY_WIDTH['small'])
        self.num_var.grid(row=0, column=1, padx=2)
        ttk.Button(self.num_var_frame, text=TRANSLATIONS[self.language]['create_fields'], 
                command=self.criar_campos_variaveis).grid(row=0, column=2, padx=2)

        # Frame para os campos das variáveis
        self.campos_frame = ttk.Frame(self.var_frame)
        self.campos_frame.grid(row=1, column=0, sticky="ew")

        # Fórmula
        ttk.Label(self.main_frame, text=TRANSLATIONS[self.language]['formula']).grid(row=4, column=0, pady=5, sticky="w")
        self.formula_entry = ttk.Entry(self.main_frame, width=ENTRY_WIDTH['formula'])
        self.formula_entry.grid(row=5, column=0, pady=5, sticky="ew")

        # Botão calcular/gerar
        self.botao_calcular = ttk.Button(self.main_frame, text=TRANSLATIONS[self.language]['calculate'], 
                                    command=self.calcular_ou_gerar)
        self.botao_calcular.grid(row=6, column=0, pady=10)
        
        # Área de resultados
        ttk.Label(self.main_frame, text=TRANSLATIONS[self.language]['results']).grid(row=7, column=0, pady=5, sticky="w")
        self.resultados_text = ScrolledText(
            self.main_frame, 
            height=12, 
            width=50,
            font=(FONT_FAMILY, FONT_SIZE)
        )
        self.resultados_text.grid(row=8, column=0, pady=5, sticky="ew")
        
        # Frame para exibir a fórmula LaTeX renderizada diretamente na interface
        self.latex_frame = ttk.Frame(self.main_frame)
        self.latex_frame.grid(row=9, column=0, pady=5, sticky="ew")
        
        self.atualizar_interface()
        self.resultados_text.delete(1.0, tk.END)
    
    def atualizar_interface(self) -> None:
        if self.modo_var.get() == "calcular":
            self.num_var_frame.grid()
            if hasattr(self, 'botao_calcular'):
                self.botao_calcular.configure(text=TRANSLATIONS[self.language]['calculate'])
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
        else:
            self.num_var_frame.grid_remove()
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
            if hasattr(self, 'botao_calcular'):
                self.botao_calcular.configure(text=TRANSLATIONS[self.language]['generate_formula'])
            # Para modo gerar, apenas um campo para lista de variáveis
            ttk.Label(self.campos_frame, text=TRANSLATIONS[self.language]['variables_list']).grid(row=0, column=0)
            self.vars_entry = ttk.Entry(self.campos_frame, width=ENTRY_WIDTH['large'])
            self.vars_entry.grid(row=0, column=1)

    def criar_campos_variaveis(self) -> None:
        try:
            num = int(self.num_var.get())
            # Limpar campos existentes
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
            # Criar campos
            self.var_entries = []
            
            # Cabeçalho das colunas
            frame = ttk.Frame(self.campos_frame)
            frame.grid(row=0, column=0, sticky="ew")
            ttk.Label(frame, text=TRANSLATIONS[self.language]['variable']).grid(row=0, column=0, padx=2)
            ttk.Label(frame, text=TRANSLATIONS[self.language]['value']).grid(row=0, column=2, padx=2)
            ttk.Label(frame, text=TRANSLATIONS[self.language]['uncertainty']).grid(row=0, column=4, padx=2)
            for i in range(num):
                frame = ttk.Frame(self.campos_frame)
                frame.grid(row=i+1, column=0, pady=2)
                ttk.Label(frame, text=f"{i+1}:").grid(row=0, column=0, padx=2)
                nome = ttk.Entry(frame, width=5)
                nome.grid(row=0, column=1, padx=2)
                valor = ttk.Entry(frame, width=10)
                valor.grid(row=0, column=3, padx=2)
                incerteza = ttk.Entry(frame, width=10)
                incerteza.grid(row=0, column=5, padx=2)
                self.var_entries.append((nome, valor, incerteza))
        except ValueError:
            messagebox.showerror("Erro", TRANSLATIONS[self.language]['invalid_vars'])

    def calcular_ou_gerar(self) -> None:
        if self.modo_var.get() == "calcular":
            self.calcular_incerteza()
        else:
            self.gerar_formula_incerteza()

    def calcular_incerteza(self) -> None:
        """Calculate uncertainty for given variables and formula"""
        if not hasattr(self, 'var_entries') or not self.var_entries:
            messagebox.showerror("Erro", TRANSLATIONS[self.language]['create_fields'])
            return

        try:
            # Collect variables
            variaveis: Dict[str, Tuple[float, float]] = {}
            for nome_entry, valor_entry, incerteza_entry in self.var_entries:
                nome = nome_entry.get()
                valor = float(valor_entry.get())
                incerteza = float(incerteza_entry.get())
                variaveis[nome] = (valor, incerteza)
                
            formula = self.formula_entry.get()
            # Replace sen -> sin for Portuguese users
            formula = formula.replace("sen", "sin")
            
            # Calculate value using math functions
            math_globals = {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "exp": math.exp, "log": math.log, "sqrt": math.sqrt, 
                "pi": math.pi
            }
            valor_final = eval(formula, math_globals,
                          {k: valor for k, (valor, _) in variaveis.items()})

            # Calculate uncertainty
            incerteza_total = self._calcular_incerteza_total(formula, variaveis)
            
            # Show results
            self._mostrar_resultados(valor_final, incerteza_total)
            
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _calcular_incerteza_total(self, formula: str, variaveis: Dict[str, Tuple[float, float]]) -> float:
        """Calculate total uncertainty using partial derivatives"""
        incerteza_total = 0
        expr = sp.sympify(formula)
        for var, (val, sigma) in variaveis.items():
            derivada = sp.diff(expr, sp.Symbol(var))
            derivada_num = float(sp.N(derivada.subs(
                {sp.Symbol(k): valor for k, (valor, _) in variaveis.items()}
            )))
            incerteza_total += (derivada_num * sigma) ** 2
        return math.sqrt(incerteza_total)
        
    def _mostrar_resultados(self, valor: float, incerteza: float) -> None:
        """Display calculation results in the text area"""
        self.resultados_text.delete(1.0, tk.END)
        self.resultados_text.insert(tk.END, f"{TRANSLATIONS[self.language]['result_header']}\n")
        self.resultados_text.insert(tk.END, f"{TRANSLATIONS[self.language]['calculated_value']} {valor:.6f}\n")
        self.resultados_text.insert(tk.END, f"{TRANSLATIONS[self.language]['total_uncertainty']} ±{incerteza:.6f}\n")
        self.resultados_text.insert(tk.END, f"{TRANSLATIONS[self.language]['final_result']} ({valor:.6f} ± {incerteza:.6f})")
        # Clear the LaTeX frame when showing calculation results
        for widget in self.latex_frame.winfo_children():
            widget.destroy()
            
    def _clear_latex_display(self):
        """Clear any LaTeX rendering from the interface"""
        for widget in self.latex_frame.winfo_children():
            widget.destroy()
        
    def _renderizar_formula_na_interface(self):
        """Render the formula using matplotlib and display it in the interface"""
        # Clear previous widget if any
        for widget in self.latex_frame.winfo_children():
            widget.destroy()
            
        # Create a formula to display
        formula = f"({self.formula_entry.get()}) \\pm \\delta"
        
        # Create a matplotlib figure to render LaTeX
        fig, ax = plt.subplots(figsize=(7, 1.5))
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula}$", fontsize=16, ha='center', va='center')
        fig.tight_layout(pad=0)
        
        # Display in the frame
        canvas = FigureCanvasTkAgg(fig, master=self.latex_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
          
    def gerar_formula_incerteza(self) -> None:
        try:
            variaveis = self.vars_entry.get().split(',')
            
            formula = self.formula_entry.get()
            formula = formula.replace("sen", "sin")   # permite também o uso de sen em português
            simbolos = {var.strip(): sp.Symbol(var.strip()) for var in variaveis}
            expr = sp.sympify(formula, locals=simbolos)
            termos = []
            for var in variaveis:
                var = var.strip()
                derivada = sp.diff(expr, simbolos[var])
                termos.append(f"({sp.latex(derivada)} \\cdot \\delta_{{{var}}})^2")
            
            formula_incerteza = "\\delta_{\\text{total}} = \\sqrt{" + " + ".join(termos) + "}"
            self.resultados_text.delete(1.0, tk.END)
            
            self.resultados_text.insert(tk.END, f"{TRANSLATIONS[self.language]['uncertainty_formula_header']}\n\n")
            self.resultados_text.insert(tk.END, f"{TRANSLATIONS[self.language]['copy_latex_code']}\n\n")
            self.resultados_text.insert(tk.END, f"{formula_incerteza}\n\n")
            
            self.formula_latex = formula_incerteza  # Guarda para visualização
            
            # Renderiza a fórmula LaTeX diretamente na interface
            self._renderizar_formula_incerteza_na_interface(formula_incerteza)
            
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            
    def _renderizar_formula_incerteza_na_interface(self, formula_latex: str):
        """Render the uncertainty formula using matplotlib and display it in the interface"""
        # Clear previous widget if any
        for widget in self.latex_frame.winfo_children():
            widget.destroy()
            
        # Create a matplotlib figure to render LaTeX
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula_latex}$", fontsize=16, ha='center', va='center')
        fig.tight_layout(pad=0)
        
        # Display in the frame
        canvas = FigureCanvasTkAgg(fig, master=self.latex_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
    def exibir_formula_latex(self, formula_latex: str) -> None:
        if not formula_latex or formula_latex.strip() == "":
            messagebox.showinfo("Atenção", TRANSLATIONS[self.language]['generate_formula'])
            return
        janela = Toplevel(self.parent)
        janela.title("Fórmula Renderizada (LaTeX)")
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula_latex}$", fontsize=18, ha='center', va='center')
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')
    def switch_language(self, language):
        """Update language for this component"""
        self.language = language
        
        # Store current values before rebuilding UI
        current_mode = self.modo_var.get() if hasattr(self, 'modo_var') else "calcular"
        current_formula = self.formula_entry.get() if hasattr(self, 'formula_entry') else ""
        current_num_vars = self.num_var.get() if hasattr(self, 'num_var') else ""
        
        # Clear and rebuild the UI with new language
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Rebuild UI
        self.setup_ui()
        
        # Restore values
        if hasattr(self, 'modo_var'):
            self.modo_var.set(current_mode)
        if hasattr(self, 'formula_entry'):
            self.formula_entry.insert(0, current_formula)
        if hasattr(self, 'num_var'):
            self.num_var.insert(0, current_num_vars)
            
        # Update interface based on mode
        self.atualizar_interface()

