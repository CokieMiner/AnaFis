"""GUI module for uncertainty calculations"""
from __future__ import annotations
from typing import List, Tuple, Dict, Optional, Union
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText
import math
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import numpy as np

from app_files.utils.type_aliases import FloatArray
from app_files.constants import TRANSLATIONS

# Constants
FONT_FAMILY = 'Courier New'
FONT_SIZE = 10
PADDING = "10"
ENTRY_WIDTH = {'small': 5, 'medium': 10, 'large': 30, 'formula': 40}

class CalculoIncertezasGUI:
    def __init__(self, root: Union[tk.Tk, tk.Toplevel], language: str = 'pt') -> None:
        self.root = root
        self.language = language
        self.root.title(TRANSLATIONS[self.language]['uncertainty_calc'])
        self.var_entries: List[Tuple[ttk.Entry, ttk.Entry, ttk.Entry]] = []
        self.criar_interface()

    def criar_interface(self) -> None:
        main_frame = ttk.Frame(self.root, padding=PADDING)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Modo de operação
        ttk.Label(main_frame, text=TRANSLATIONS[self.language]['operation_mode']).grid(row=0, column=0, pady=5, sticky="w")
        self.modo_var = tk.StringVar(value="calcular")
        ttk.Radiobutton(main_frame, text=TRANSLATIONS[self.language]['calc_value_uncertainty'], 
                    variable=self.modo_var, value="calcular", 
                    command=self.atualizar_interface).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(main_frame, text=TRANSLATIONS[self.language]['generate_uncertainty_formula'],
                    variable=self.modo_var, value="gerar",
                    command=self.atualizar_interface).grid(row=2, column=0, sticky="w")

        # Frame para entrada de variáveis
        self.var_frame = ttk.LabelFrame(main_frame, text=TRANSLATIONS[self.language]['variables_list'], padding="5")
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
        ttk.Label(main_frame, text=TRANSLATIONS[self.language]['formula']).grid(row=4, column=0, pady=5, sticky="w")
        self.formula_entry = ttk.Entry(main_frame, width=ENTRY_WIDTH['formula'])
        self.formula_entry.grid(row=5, column=0, pady=5, sticky="ew")

        # Botão calcular/gerar
        self.botao_calcular = ttk.Button(main_frame, text=TRANSLATIONS[self.language]['calculate'], 
                                    command=self.calcular_ou_gerar)
        self.botao_calcular.grid(row=6, column=0, pady=10)

        # Área de resultados
        ttk.Label(main_frame, text=TRANSLATIONS[self.language]['results']).grid(row=7, column=0, pady=5, sticky="w")
        self.resultados_text = ScrolledText(
            main_frame, 
            height=12, 
            width=50,
            font=(FONT_FAMILY, FONT_SIZE)
        )
        self.resultados_text.grid(row=8, column=0, pady=5, sticky="ew")

        # Botões de copiar fórmula e exibir LaTeX (inicialmente ocultos)
        self.botao_copiar_formula = ttk.Button(main_frame, text=TRANSLATIONS[self.language]['copy_formula'], 
            command=self.copiar_formula)
        self.botao_exibir_latex = ttk.Button(main_frame, text=TRANSLATIONS[self.language]['show_latex'], 
            command=lambda: self.exibir_formula_latex(getattr(self, 'formula_latex', r'')))

        self.atualizar_interface()
        self.resultados_text.delete(1.0, tk.END)

    def copiar_formula(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.resultados_text.get(1.0, tk.END))

    def atualizar_interface(self) -> None:
        if self.modo_var.get() == "calcular":
            self.num_var_frame.grid()
            if hasattr(self, 'botao_calcular'):
                self.botao_calcular.configure(text=TRANSLATIONS[self.language]['calculate'])
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
            # Esconde os botões extras
            self.botao_copiar_formula.grid_remove()
            self.botao_exibir_latex.grid_remove()
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
            # Mostra os botões extras logo abaixo do resultados_text
            self.botao_copiar_formula.grid(row=9, column=0, pady=5)
            self.botao_exibir_latex.grid(row=10, column=0, pady=5)

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
            ttk.Label(frame, text=TRANSLATIONS[self.language]['variable']).grid(row=0, column=0)
            ttk.Label(frame, text='&').grid(row=0, column=1)
            ttk.Label(frame, text=TRANSLATIONS[self.language]['value']).grid(row=0, column=2)
            ttk.Label(frame, text='±').grid(row=0, column=3)
            ttk.Label(frame, text=TRANSLATIONS[self.language]['uncertainty']).grid(row=0, column=4)
            for i in range(num):
                frame = ttk.Frame(self.campos_frame)
                frame.grid(row=i+1, column=0, pady=2)
                ttk.Label(frame, text=TRANSLATIONS[self.language]['variable'] + f" {i+1}:").grid(row=0, column=0)
                nome = ttk.Entry(frame, width=5)
                nome.grid(row=0, column=1)
                ttk.Label(frame, text=TRANSLATIONS[self.language]['value']).grid(row=0, column=2)
                valor = ttk.Entry(frame, width=10)
                valor.grid(row=0, column=3)
                ttk.Label(frame, text=TRANSLATIONS[self.language]['uncertainty']).grid(row=0, column=4)
                incerteza = ttk.Entry(frame, width=10)
                incerteza.grid(row=0, column=5)
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
        self.resultados_text.insert(tk.END, "=== Resultado ===\n")
        self.resultados_text.insert(tk.END, f"Valor calculado: {valor:.6f}\n")
        self.resultados_text.insert(tk.END, f"Incerteza total: ±{incerteza:.6f}\n")
        self.resultados_text.insert(tk.END, f"Resultado final: ({valor:.6f} ± {incerteza:.6f})")

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
                termos.append(f"(\\sigma_{{{var}}} \\cdot {sp.latex(derivada)})^2")
            formula_incerteza = "\\sigma_{\\text{total}} = \\sqrt{" + " + ".join(termos) + "}"
            self.resultados_text.delete(1.0, tk.END)
            self.resultados_text.insert(tk.END, "=== Fórmula de Incerteza (LaTeX) ===\n\n")
            self.resultados_text.insert(tk.END, "Copie o código abaixo para LaTeX:\n\n")
            self.resultados_text.insert(tk.END, f"{formula_incerteza}\n\n")
            self.resultados_text.insert(tk.END, "Clique em 'Exibir em LaTeX' para visualizar a fórmula renderizada.\n")
            self.formula_latex = formula_incerteza  # Guarda para visualização
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def exibir_formula_latex(self, formula_latex: str) -> None:
        if not formula_latex or formula_latex.strip() == "":
            messagebox.showinfo("Atenção", TRANSLATIONS[self.language]['generate_formula'])
            return
        janela = Toplevel(self.root)
        janela.title("Fórmula Renderizada (LaTeX)")
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula_latex}$", fontsize=18, ha='center', va='center')
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

