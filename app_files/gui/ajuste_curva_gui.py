"""GUI module for curve fitting"""
from __future__ import annotations
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from typing import List, Optional, Callable, Union
import numpy as np
import sympy as sp
from scipy.odr import ODR, Model, RealData
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

from app_files.models import ODRModelImplementation
from app_files.constants import TRANSLATIONS

class AjusteCurvaGUI:
    def __init__(self, root: Union[tk.Tk, tk.Toplevel], language: str = 'pt') -> None:
        self.root = root
        self.language = language
        self.root.title(TRANSLATIONS[self.language]['curve_fitting_title'])
        
        # Initialize instance variables
        self.x: np.ndarray = np.array([])
        self.y: np.ndarray = np.array([])
        self.sigma_x: np.ndarray = np.array([])
        self.sigma_y: np.ndarray = np.array([])
        self.cabecalho: List[str] = []
        self.modelo: Optional[Callable] = None
        
        # Setup matplotlib
        fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=6, padx=5, pady=5)
        
        self.odr: Optional[ODR] = None
        self.parametros: List[sp.Symbol] = []
        
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the user interface"""
        self.root.geometry("1200x800")
        
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Data input frame
        data_frame = ttk.LabelFrame(main_frame, text=TRANSLATIONS[self.language]['data_input'])
        data_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # File selection
        ttk.Label(data_frame, text=TRANSLATIONS[self.language]['data_file']).grid(row=0, column=0)
        self.file_entry = ttk.Entry(data_frame, width=40)
        self.file_entry.grid(row=0, column=1, padx=5)
        ttk.Button(data_frame, text=TRANSLATIONS[self.language]['browse'],
                  command=self.browse_file).grid(row=0, column=2)
                  
        # Equation and parameters frame
        params_frame = ttk.LabelFrame(main_frame, text=TRANSLATIONS[self.language]['fitting_parameters'])
        params_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(params_frame, text=TRANSLATIONS[self.language]['equation']).grid(row=0, column=0)
        self.equation_entry = ttk.Entry(params_frame, width=40)
        self.equation_entry.grid(row=0, column=1, padx=5)
        
        # Numerical settings frame
        num_settings_frame = ttk.Frame(params_frame)
        num_settings_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(num_settings_frame, text=TRANSLATIONS[self.language]['max_iterations']).grid(row=0, column=0)
        self.max_iter_entry = ttk.Entry(num_settings_frame, width=8)
        self.max_iter_entry.insert(0, "1000")
        self.max_iter_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(num_settings_frame, text=TRANSLATIONS[self.language]['num_points']).grid(row=0, column=2)
        self.num_points_entry = ttk.Entry(num_settings_frame, width=8)
        self.num_points_entry.insert(0, "1000")
        self.num_points_entry.grid(row=0, column=3, padx=5)
        
        # Graph settings frame
        graph_settings_frame = ttk.LabelFrame(main_frame, text=TRANSLATIONS[self.language]['graph_settings'])
        graph_settings_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['title']).grid(row=0, column=0)
        self.title_entry = ttk.Entry(graph_settings_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['x_label']).grid(row=1, column=0, padx=5, pady=5)
        self.x_label_var = tk.StringVar(value="X")
        x_entry = ttk.Entry(graph_settings_frame, textvariable=self.x_label_var, width=40)
        x_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['y_label']).grid(row=2, column=0, padx=5, pady=5)
        self.y_label_var = tk.StringVar(value="Y")
        y_entry = ttk.Entry(graph_settings_frame, textvariable=self.y_label_var, width=40)
        y_entry.grid(row=2, column=1, padx=5, pady=5)        
        
        scales_frame = ttk.Frame(graph_settings_frame)
        scales_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Label(scales_frame, text=TRANSLATIONS[self.language]['x_scale']).grid(row=0, column=0)
        self.x_scale = ttk.Combobox(scales_frame, values=[TRANSLATIONS[self.language]['linear'], TRANSLATIONS[self.language]['log']], state="readonly", width=8)
        self.x_scale.set(TRANSLATIONS[self.language]['linear'])
        self.x_scale.grid(row=0, column=1, padx=5)
        
        ttk.Label(scales_frame, text=TRANSLATIONS[self.language]['y_scale']).grid(row=0, column=2)
        self.y_scale = ttk.Combobox(scales_frame, values=[TRANSLATIONS[self.language]['linear'], TRANSLATIONS[self.language]['log']], state="readonly", width=8)
        self.y_scale.set(TRANSLATIONS[self.language]['linear'])
        self.y_scale.grid(row=0, column=3, padx=5)
        
        # Initial estimates frame
        self.estimates_frame = ttk.LabelFrame(main_frame, text=TRANSLATIONS[self.language]['initial_estimates'])
        self.estimates_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text=TRANSLATIONS[self.language]['progress'])
        progress_frame.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        
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
        results_frame = ttk.LabelFrame(main_frame, text=TRANSLATIONS[self.language]['results'])
        results_frame.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        
        self.results_text = ScrolledText(results_frame, height=8, width=40)
        self.results_text.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Action buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Button(
            buttons_frame, 
            text=TRANSLATIONS[self.language]['perform_fit'],
            style="Accent.TButton",
            command=self.perform_fit
        ).grid(row=0, column=0, pady=5, padx=5, sticky="ew")
        
        ttk.Button(
            buttons_frame,
            text=TRANSLATIONS[self.language]['save_graph'],
            command=self.save_graph
        ).grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        
        # Configure column weights
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        # Bindings
        self.equation_entry.bind("<FocusOut>", lambda e: self.update_estimates_frame())
        self.x_scale.bind('<<ComboboxSelected>>', lambda e: self.update_scales())
        self.y_scale.bind('<<ComboboxSelected>>', lambda e: self.update_scales())

    def update_scales(self):
        if self.x_scale.get() == TRANSLATIONS[self.language]['log']:
            self.ax.set_xscale('log')
        else:
            self.ax.set_xscale('linear')
            
        if self.y_scale.get() == TRANSLATIONS[self.language]['log']:
            self.ax.set_yscale('log')
        else:
            self.ax.set_yscale('linear')
       
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title=TRANSLATIONS[self.language]['select_data_file'],
            filetypes=[("Text or CSV files", "*.txt *.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            
    def save_graph(self):
        """Save the graph to a file"""
        filename = filedialog.asksaveasfilename(
            title=TRANSLATIONS[self.language]['save_file'],
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.canvas.figure.savefig(filename)

    def update_estimates_frame(self):
        """Update the estimates frame based on the equation"""
        # Clear current frame
        for widget in self.estimates_frame.winfo_children():
            widget.destroy()

        try:
            equation = self.equation_entry.get().replace('^', '**')
            if '=' in equation:
                equation = equation.split('=')[1].strip()

            x_sym = sp.Symbol('x')
            expr = sp.sympify(equation)
            self.parametros = sorted(list(expr.free_symbols - {x_sym}), key=lambda s: s.name)

            # Create input fields for each parameter
            for i, param in enumerate(self.parametros):
                ttk.Label(self.estimates_frame, text=f"{param}:").grid(row=i, column=0, padx=5, pady=2)
                entry = ttk.Entry(self.estimates_frame, width=10)
                entry.insert(0, "1.0")
                entry.grid(row=i, column=1, padx=5, pady=2)
                setattr(self, f"estimate_{param}", entry)

        except Exception as e:
            messagebox.showerror(
                TRANSLATIONS[self.language]['error'],
                TRANSLATIONS[self.language]['invalid_formula'].format(error=str(e))
            )

    def read_file(self, file_name):
        error_messages = {
            'file_not_found': {
                'pt': "O arquivo '{file}' não foi encontrado.",
                'en': "The file '{file}' was not found."
            },
            'processing_error': {
                'pt': "Erro ao processar o arquivo: {error}",
                'en': "Error processing the file: {error}"
            }
        }

        if not os.path.isfile(file_name):
            messagebox.showerror(
                TRANSLATIONS[self.language]['error'],
                error_messages['file_not_found'][self.language].format(file=file_name)
            )
            raise FileNotFoundError(error_messages['file_not_found'][self.language].format(file=file_name))

        try:
            # Detecta o tipo de separador pelo sufixo do arquivo
            _, ext = os.path.splitext(file_name)
            if ext.lower() == ".csv":
                delimiter = ','
            else:
                delimiter = '\t'

            with open(file_name, 'r') as f:
                header = f.readline()
                lines = f.readlines()
            if len(lines) == 0:
                messagebox.showerror("Erro ao ler arquivo", "O arquivo está vazio ou só contém o cabeçalho.")
                raise ValueError("O arquivo está vazio ou só contém o cabeçalho.")

            # Checa número de colunas de forma genérica (funciona para ambos formatos)
            for i, line in enumerate(lines):
                parts = line.strip().split(delimiter)
                if len(parts) != 4:
                    messagebox.showerror("Erro ao ler arquivo",
                        f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")
                    raise ValueError(f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")
            # Carrega dados usando numpy
            dados = np.genfromtxt(file_name, delimiter=delimiter, skip_header=1, dtype=str)
            dados = np.char.replace(dados, ',', '.')
            x = dados[:, 0].astype(float)
            sigma_x = dados[:, 1].astype(float)
            y = dados[:, 2].astype(float)
            sigma_y = dados[:, 3].astype(float)
            return x, sigma_x, y, sigma_y
        except Exception as e:
            messagebox.showerror(
                TRANSLATIONS[self.language]['error'],
                error_messages['processing_error'][self.language].format(error=str(e))
            )
            raise

    
    def create_model(self, equation, parameters):
        x = sp.Symbol('x')
        expr = sp.sympify(equation)
        
        derivadas = [sp.diff(expr, p) for p in parameters]
        
        modelo_numerico = sp.lambdify((parameters, x), expr, 'numpy')
        derivadas_numericas = [sp.lambdify((parameters, x), d, 'numpy') for d in derivadas]
        
        return modelo_numerico, derivadas_numericas
    
    def perform_fit(self):
        try:
            num_points = int(self.num_points_entry.get())
            if num_points <= 0:
                raise ValueError(TRANSLATIONS[self.language]['positive_points'])
        except ValueError as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], TRANSLATIONS[self.language]['invalid_points'])
            return
        try:
            # Reset progress and status
            self.progress_var.set(0)
            self.status_label.config(text=TRANSLATIONS[self.language]['starting_fit'])
            self.root.update()

            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Update estimates if needed
            if not self.parametros:
                self.update_estimates_frame()
            
            # Get field values
            caminho = self.file_entry.get()
            equacao = self.equation_entry.get().replace('^', '**')
            if '=' in equacao:
                equacao = equacao.split('=')[1].strip()
            max_iter = int(self.max_iter_entry.get())
            
            # Get initial estimates
            chute = []
            for param in self.parametros:
                entry = getattr(self, f"estimate_{param}")
                chute.append(float(entry.get()))
                
            # Load data
            self.x, self.sigma_x, self.y, self.sigma_y = self.read_file(caminho)
            with open(caminho, 'r') as f:
                self.cabecalho = f.readline().strip().split('\t')
                
            # Create model
            self.modelo, derivadas = self.create_model(equacao, self.parametros)
            if self.modelo is None:
                raise RuntimeError("Model function is not initialized.")
            modelo_odr = Model(ODRModelImplementation(self.modelo, derivadas))
            self.equacao = equacao

            # Execute ODR
            dados = RealData(self.x, self.y, sx=self.sigma_x, sy=self.sigma_y)
            self.odr = ODR(dados, modelo_odr, beta0=chute, maxit=max_iter)
            
            def run_odr():
                try:
                    if self.odr is not None:
                        resultado = self.odr.run()
                        self.root.after(0, lambda: self.mostrar_resultados(resultado))
                        self.root.after(0, lambda: self.status_label.config(text=TRANSLATIONS[self.language]['fit_complete']))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(TRANSLATIONS[self.language]['error'], f"{TRANSLATIONS[self.language]['fit_error']}: {str(e)}"))
                    self.root.after(0, lambda: self.status_label.config(text=TRANSLATIONS[self.language]['fit_error']))

            def update_progress():
                if self.odr is not None and hasattr(self.odr, 'iwork') and self.odr.iwork is not None:
                    try:
                        current_iter = self.odr.iwork[0]
                        self.progress_var.set(min(100, current_iter * 10))
                        self.status_label.config(text=f"Iteração: {current_iter}")
                        if current_iter < max_iter:
                            self.root.after(100, update_progress)
                    except:
                        pass
                else:
                    self.root.after(100, update_progress)

            # Start progress updates
            self.root.after(100, update_progress)
            
            # Start ODR in separate thread
            threading.Thread(target=run_odr, daemon=True).start()

        except Exception as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], f"{TRANSLATIONS[self.language]['fit_error']}: {str(e)}")
            self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['verify_and_retry']}\n")

    def mostrar_resultados(self, resultado):
        try:
            # Calcular estatísticas
            if self.modelo is None:
                raise RuntimeError("Model function is not initialized.")
            y_pred = self.modelo(resultado.beta, self.x)
            chi2_total = np.sum(((self.y - y_pred) / self.sigma_y) ** 2)
            r2 = 1 - np.sum((self.y - y_pred) ** 2) / np.sum((self.y - np.mean(self.y)) ** 2)
            # Mostrar resultados
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"=== {TRANSLATIONS[self.language]['results']} ===\n")
            for p, v, e in zip(self.parametros, resultado.beta, resultado.sd_beta):
                self.results_text.insert(tk.END, f"{p} = {v:.6f} ± {e:.6f}\n")
            self.results_text.insert(tk.END, f"\n{TRANSLATIONS[self.language]['chi_squared']}: {chi2_total:.2f}\n")
            self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['reduced_chi_squared']}: {resultado.res_var:.2f}\n")
            self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['r_squared']}: {r2:.4f}\n")
            
            # Atualizar gráfico
            self.ax.clear()
            self.ax.errorbar(self.x, self.y, xerr=self.sigma_x, yerr=self.sigma_y, fmt='o', label=TRANSLATIONS[self.language]['data_points'])
            num_points = int(self.num_points_entry.get())
            x_fit = np.linspace(min(self.x), max(self.x), num_points)
            self.ax.plot(x_fit, self.modelo(resultado.beta, x_fit), 'r-', label=TRANSLATIONS[self.language]['fit_curve'])
            
            # Atualizar escalas antes de plotar
            self.update_scales()
            
            # Título e labels
            if self.title_entry.get():
                self.ax.set_title(self.title_entry.get())
            self.ax.set_xlabel(self.x_label_var.get())
            self.ax.set_ylabel(self.y_label_var.get())
            self.ax.legend()
            self.ax.grid(True)
            
            # Adicionar caixa de texto com informações
            texto_info = f"{TRANSLATIONS[self.language]['equation']}: y = {self.equacao}\n"
            texto_info += '\n'.join([f"{p} = {v:.6f} ± {e:.6f}" for p, v, e in zip(self.parametros, resultado.beta, resultado.sd_beta)])
            texto_info += f"\n{TRANSLATIONS[self.language]['chi_squared']}: {chi2_total:.2f}\n{TRANSLATIONS[self.language]['reduced_chi_squared']}: {resultado.res_var:.2f}\n{TRANSLATIONS[self.language]['r_squared']}: {r2:.4f}"
            self.ax.text(
                0.98, 0.02,
                texto_info,
                transform=self.ax.transAxes,
                fontsize=7,
                bbox=dict(facecolor='white', alpha=0.5),
                ha='right',
                va='bottom'
            )
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], f"Erro ao mostrar resultados: {str(e)}")