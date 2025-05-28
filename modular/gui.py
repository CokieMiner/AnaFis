"""GUI components for AnaFis"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sympy as sp
import threading
from typing import List, Tuple

from models import ProgressTracker
from regression import RegressionAnalyzer
from uncertainties import UncertaintyCalculator

class BaseGUI:
    """Base GUI class"""
    def __init__(self, root: tk.Tk | tk.Toplevel) -> None:
        self.root = root
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the user interface"""
        raise NotImplementedError

class AjusteCurvaGUI(BaseGUI):
    """Curve fitting interface"""
    def __init__(self, root: tk.Tk | tk.Toplevel) -> None:
        self.root = root
        self.root.title("Ajuste de Curvas")
        self.root.geometry("1200x800")
        
        self.analyzer = RegressionAnalyzer()
        self.fig = Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        
        self.criar_interface()
        
    def criar_interface(self) -> None:
        """Create the interface"""
        # Create main frames
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Split into left and right panels
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.criar_painel_controles(left_panel)
        self.criar_painel_grafico(right_panel)

    def criar_painel_controles(self, parent: ttk.Frame) -> None:
        """Create control panel"""
        # File loading section
        file_frame = ttk.LabelFrame(parent, text="Arquivo de Dados")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        ttk.Button(
            file_frame,
            text="Procurar",
            command=self.carregar_arquivo
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # Model definition section
        model_frame = ttk.LabelFrame(parent, text="Modelo")
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(model_frame, text="Equação:").pack(padx=5, pady=2)
        self.equation_entry = ttk.Entry(model_frame)
        self.equation_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # Parameters section
        self.param_frame = ttk.LabelFrame(parent, text="Parâmetros")
        self.param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Fit control section
        control_frame = ttk.LabelFrame(parent, text="Controle")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Realizar Ajuste",
            command=self.realizar_ajuste
        ).pack(fill=tk.X, padx=5, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(parent, text="Resultados")
        results_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.results_text = ScrolledText(results_frame, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def criar_painel_grafico(self, parent: ttk.Frame) -> None:
        """Create graph panel"""
        frame = ttk.LabelFrame(parent, text="Gráfico")
        frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = FigureCanvasTkAgg(self.fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar_frame = ttk.Frame(frame)
        toolbar_frame.pack(fill=tk.X)
        
        ttk.Button(
            toolbar_frame,
            text="Salvar Gráfico",
            command=self.salvar_grafico
        ).pack(side=tk.RIGHT, padx=5, pady=5)

    def carregar_arquivo(self) -> None:
        """Load data file"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Dados", "*.txt *.csv"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if filename:
            try:
                x, sx, y, sy = self.analyzer.ler_arquivo(filename)
                self.atualizar_grafico(x, y, sx, sy)
                self.file_entry.delete(0, tk.END)
                self.file_entry.insert(0, filename)
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def atualizar_grafico(self, x, y, sx, sy) -> None:
        """Update plot with new data"""
        self.ax.clear()
        self.ax.errorbar(x, y, xerr=sx, yerr=sy, fmt='o', label='Dados')
        self.ax.legend()
        self.ax.grid(True)
        self.fig.canvas.draw()

    def realizar_ajuste(self) -> None:
        """Perform curve fitting"""
        # Implementation here
        pass

    def salvar_grafico(self) -> None:
        """Save plot to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("PDF", "*.pdf"),
                ("SVG", "*.svg")
            ]
        )
        if filename:
            try:
                self.fig.savefig(filename, bbox_inches='tight', dpi=300)
                messagebox.showinfo(
                    "Sucesso",
                    "Gráfico salvo com sucesso!"
                )
            except Exception as e:
                messagebox.showerror("Erro", str(e))

class CalculoIncertezasGUI(BaseGUI):
    """Uncertainty calculation interface"""
    def __init__(self, root: tk.Tk | tk.Toplevel) -> None:
        self.root = root
        self.root.title("Cálculo de Incertezas")
        self.var_entries: List[Tuple[ttk.Entry, ttk.Entry, ttk.Entry]] = []
        self.calculator = UncertaintyCalculator()
        
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Modo")
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.mode_var = tk.StringVar(value="calc")
        ttk.Radiobutton(
            mode_frame,
            text="Calcular",
            value="calc",
            variable=self.mode_var,
            command=self.update_mode
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            mode_frame,
            text="Gerar Fórmula",
            value="form",
            variable=self.mode_var,
            command=self.update_mode
        ).pack(side=tk.LEFT, padx=5)
        
        # Variables section
        self.vars_frame = ttk.LabelFrame(main_frame, text="Variáveis")
        self.vars_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            self.vars_frame,
            text="Adicionar Variável",
            command=self.add_variable
        ).pack(padx=5, pady=5)
        
        # Formula section
        formula_frame = ttk.LabelFrame(main_frame, text="Fórmula")
        formula_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.formula_entry = ttk.Entry(formula_frame)
        self.formula_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Resultados")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = ScrolledText(results_frame)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Calcular",
            command=self.calculate
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Limpar",
            command=self.clear
        ).pack(side=tk.LEFT, padx=5)

    def update_mode(self) -> None:
        """Update interface based on selected mode"""
        pass

    def add_variable(self) -> None:
        """Add new variable row"""
        row = len(self.var_entries) + 1
        frame = ttk.Frame(self.vars_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        name = ttk.Entry(frame, width=10)
        name.pack(side=tk.LEFT, padx=2)
        
        value = ttk.Entry(frame, width=10)
        value.pack(side=tk.LEFT, padx=2)
        
        uncert = ttk.Entry(frame, width=10)
        uncert.pack(side=tk.LEFT, padx=2)
        
        self.var_entries.append((name, value, uncert))

    def calculate(self) -> None:
        """Perform calculation"""
        if self.mode_var.get() == "calc":
            self.calculate_value()
        else:
            self.generate_formula()

    def calculate_value(self) -> None:
        """Calculate value and uncertainty"""
        pass

    def generate_formula(self) -> None:
        """Generate uncertainty formula"""
        pass

    def clear(self) -> None:
        """Clear all fields"""
        pass