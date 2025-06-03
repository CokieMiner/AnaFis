"""GUI module for curve fitting"""

from __future__ import annotations

import os

import threading

import tkinter as tk

from tkinter import ttk, messagebox, filedialog

from tkinter.scrolledtext import ScrolledText

from typing import List, Optional, Callable, Union, Dict, Any

import numpy as np

import sympy as sp

from scipy.odr import ODR, Model, RealData

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib import pyplot as plt

import json

import pandas as pd



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

        

        # Setup matplotlib with subplots for main plot and residuals

        plt.style.use('default')  # Use default style

        self.fig, (self.ax, self.ax_res) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)

        

        self.odr: Optional[ODR] = None

        self.parametros: List[sp.Symbol] = []

        

        # Model cache and history

        self.model_cache: Dict[str, Any] = {}

        self.history: List[Dict[str, Any]] = []

        self.history_index: int = -1

        

        # Preset models

        self.preset_models = {

            "Linear: a*x + b": "a*x + b",

            "Quadrático: a*x² + b*x + c": "a*x**2 + b*x + c", 

            "Exponencial: a*exp(b*x)": "a*exp(b*x)",

            "Logarítmico: a*log(x) + b": "a*log(x) + b",

            "Potência: a*x^b": "a*x**b",

            "Senoidal: a*sin(b*x + c) + d": "a*sin(b*x + c) + d"

        }

        

        self.setup_ui()

        # Initialize empty plot after UI is set up

        self.root.after(100, self.initialize_empty_plot)



    def initialize_empty_plot(self):

        """Initialize empty plot with proper axes setup"""

        self.ax.clear()

        self.ax_res.clear()

        

        # Setup empty main plot

        self.ax.set_xlabel("X")

        self.ax.set_ylabel("Y")

        self.ax.grid(True, alpha=0.3)

        

        # Setup empty residuals plot

        self.ax_res.set_xlabel("X")

        self.ax_res.set_ylabel('Resíduos')

        self.ax_res.grid(True, alpha=0.3)

        self.ax_res.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        

        self.fig.tight_layout()

        self.canvas.draw()



    def update_data_preview(self, data):

        """Update data preview text widget - showing all data"""

        self.data_text.delete(1.0, tk.END)

        preview_str = data.to_string(index=False, float_format='%.4f')

        self.data_text.insert(1.0, preview_str)

        # Update plot with data immediately

        self.plot_data_only()



    def plot_data_only(self):

        """Plot only the data points without fit curve"""

        if len(self.x) == 0 or len(self.y) == 0:

            return

            

        self.ax.clear()

        self.ax_res.clear()

        

        # Plot data points

        self.ax.errorbar(self.x, self.y, xerr=self.sigma_x, yerr=self.sigma_y, 

                        fmt='o', label=TRANSLATIONS[self.language]['data_points'])

        

        # Setup axes

        if hasattr(self, 'title_entry') and self.title_entry.get():

            self.ax.set_title(self.title_entry.get())

        self.ax.set_xlabel(self.x_label_var.get() if hasattr(self, 'x_label_var') else "X")

        self.ax.set_ylabel(self.y_label_var.get() if hasattr(self, 'y_label_var') else "Y")

        self.ax.legend()

        self.ax.grid(True, alpha=0.3)

        

        # Setup residuals plot (empty for now)

        self.ax_res.set_xlabel(self.x_label_var.get() if hasattr(self, 'x_label_var') else "X")

        self.ax_res.set_ylabel('Resíduos')

        self.ax_res.grid(True, alpha=0.3)

        self.ax_res.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        
         # Apply scales

        if hasattr(self, 'x_scale') and hasattr(self, 'y_scale'):

            self.update_scales()

        

        self.fig.tight_layout()

        self.canvas.draw()



    def setup_ui(self) -> None:

        """Set up the user interface"""

        self.root.geometry("1400x900")

        

        # Configure root grid

        self.root.rowconfigure(0, weight=1)

        self.root.columnconfigure(0, weight=1)

        self.root.columnconfigure(1, weight=2)

        

        # Create main paned window

        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)

        main_paned.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        

        # Left panel for controls

        control_frame = ttk.Frame(main_paned, padding="5")

        main_paned.add(control_frame, weight=1)

        

        # Right panel for plots

        plot_frame = ttk.Frame(main_paned)

        main_paned.add(plot_frame, weight=2)

        

        # Setup plot canvas

        canvas_widget = self.canvas.get_tk_widget()

        canvas_widget.pack(in_=plot_frame, fill=tk.BOTH, expand=True)

        

        # Create vertical paned window for control sections

        control_paned = ttk.PanedWindow(control_frame, orient=tk.VERTICAL)

        control_paned.pack(fill=tk.BOTH, expand=True)

        

        # Data input frame

        data_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['data_input'])

        control_paned.add(data_frame, weight=1)

        

        # File selection

        ttk.Label(data_frame, text=TRANSLATIONS[self.language]['data_file']).grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.file_entry = ttk.Entry(data_frame, width=40)

        self.file_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Button(data_frame, text=TRANSLATIONS[self.language]['browse'],

                  command=self.browse_file).grid(row=0, column=2, padx=5, pady=2)

        

        # Data preview frame

        preview_frame = ttk.LabelFrame(data_frame, text="Dados Carregados")

        preview_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.data_text = ScrolledText(preview_frame, height=8, width=50)

        self.data_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                  

        # Equation and parameters frame

        params_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['fitting_parameters'])

        control_paned.add(params_frame, weight=1)

        

        # Model presets

        ttk.Label(params_frame, text="Modelo Pré-definido:").grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.model_selector = ttk.Combobox(params_frame, 

                                         values=list(self.preset_models.keys()),

                                         state="readonly",

                                         width=37)

        self.model_selector.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        self.model_selector.bind("<<ComboboxSelected>>", self.apply_preset_model)

        

        ttk.Label(params_frame, text=TRANSLATIONS[self.language]['equation']).grid(row=1, column=0, sticky="w", padx=5, pady=2)

        self.equation_entry = ttk.Entry(params_frame, width=40)

        self.equation_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        self.equation_entry.bind("<KeyRelease>", self.validate_equation)

        self.equation_entry.bind("<FocusOut>", lambda e: self.update_estimates_frame())

        

        # Numerical settings frame

        num_settings_frame = ttk.Frame(params_frame)

        num_settings_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

        

        ttk.Label(num_settings_frame, text=TRANSLATIONS[self.language]['max_iterations']).grid(row=0, column=0, padx=5)

        self.max_iter_entry = ttk.Entry(num_settings_frame, width=8)

        self.max_iter_entry.insert(0, "1000")

        self.max_iter_entry.grid(row=0, column=1, padx=5)

        

        ttk.Label(num_settings_frame, text=TRANSLATIONS[self.language]['num_points']).grid(row=0, column=2, padx=5)

        self.num_points_entry = ttk.Entry(num_settings_frame, width=8)

        self.num_points_entry.insert(0, "1000")

        self.num_points_entry.grid(row=0, column=3, padx=5)

        

        # Initial estimates frame

        self.estimates_frame = ttk.LabelFrame(params_frame, text=TRANSLATIONS[self.language]['initial_estimates'])

        self.estimates_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        

        # Graph settings frame

        graph_settings_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['graph_settings'])

        control_paned.add(graph_settings_frame, weight=1)

        

        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['title']).grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.title_entry = ttk.Entry(graph_settings_frame, width=40)

        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        

        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['x_label']).grid(row=1, column=0, sticky="w", padx=5, pady=2)

        self.x_label_var = tk.StringVar(value="X")

        x_entry = ttk.Entry(graph_settings_frame, textvariable=self.x_label_var, width=40)

        x_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        

        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['y_label']).grid(row=2, column=0, sticky="w", padx=5, pady=2)

        self.y_label_var = tk.StringVar(value="Y")

        y_entry = ttk.Entry(graph_settings_frame, textvariable=self.y_label_var, width=40)

        y_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")      

        

        scales_frame = ttk.Frame(graph_settings_frame)

        scales_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        

        ttk.Label(scales_frame, text=TRANSLATIONS[self.language]['x_scale']).grid(row=0, column=0, padx=5)

        self.x_scale = ttk.Combobox(scales_frame, values=[TRANSLATIONS[self.language]['linear'], TRANSLATIONS[self.language]['log']], state="readonly", width=8)

        self.x_scale.set(TRANSLATIONS[self.language]['linear'])

        self.x_scale.grid(row=0, column=1, padx=5)

        self.x_scale.bind('<<ComboboxSelected>>', lambda e: self.update_scales())

        

        ttk.Label(scales_frame, text=TRANSLATIONS[self.language]['y_scale']).grid(row=0, column=2, padx=5)

        self.y_scale = ttk.Combobox(scales_frame, values=[TRANSLATIONS[self.language]['linear'], TRANSLATIONS[self.language]['log']], state="readonly", width=8)

        self.y_scale.set(TRANSLATIONS[self.language]['linear'])

        self.y_scale.grid(row=0, column=3, padx=5)

        self.y_scale.bind('<<ComboboxSelected>>', lambda e: self.update_scales())

        

        # Progress frame

        progress_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['progress'])

        control_paned.add(progress_frame, weight=1)

        

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

        results_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['results'])

        control_paned.add(results_frame, weight=2)

        

        self.results_text = ScrolledText(results_frame, height=8, width=40)

        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        

        # Action buttons frame

        buttons_frame = ttk.Frame(results_frame)

        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        

        ttk.Button(

            buttons_frame, 

            text=TRANSLATIONS[self.language]['perform_fit'],

            command=self.perform_fit

        ).grid(row=0, column=0, pady=5, padx=2, sticky="ew")

        

        ttk.Button(

            buttons_frame,

            text=TRANSLATIONS[self.language]['save_graph'],

            command=self.save_graph

        ).grid(row=0, column=1, pady=5, padx=2, sticky="ew")

        

        ttk.Button(

            buttons_frame,

            text="Exportar Dados",

            command=self.export_results

        ).grid(row=0, column=2, pady=5, padx=2, sticky="ew")

        

        # History navigation frame

        nav_frame = ttk.Frame(buttons_frame)

        nav_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")

        

        ttk.Button(nav_frame, text="◀ Anterior", command=self.prev_fit).pack(side="left", padx=2)

        ttk.Button(nav_frame, text="Próximo ▶", command=self.next_fit).pack(side="left", padx=2)

        self.history_label = ttk.Label(nav_frame, text="Histórico: 0/0")

        self.history_label.pack(side="left", padx=10)

        

        # Configure column weights

        for i in range(3):

            buttons_frame.columnconfigure(i, weight=1)

        # Configure frame column weights for proper resizing

        data_frame.columnconfigure(1, weight=1)

        

    def browse_file(self):

        """Browse for data file - default to all compatible formats"""

        filename = filedialog.askopenfilename(

            title=TRANSLATIONS[self.language]['select_data_file'],

            filetypes=[

                ("Todos os compatíveis", "*.xlsx;*.xls;*.txt;*.csv;*.json"),

                ("Excel files", "*.xlsx *.xls"),

                ("Text or CSV files", "*.txt *.csv"), 

                ("JSON files", "*.json"),

                ("All files", "*.*")

            ]

        )

        if filename:

            self.file_entry.delete(0, tk.END)

            self.file_entry.insert(0, filename)

            # Automatically load data when file is selected

            try:

                self.x, self.sigma_x, self.y, self.sigma_y = self.read_file(filename)

                with open(filename, 'r', encoding='utf-8') as f:

                    try:

                        self.cabecalho = f.readline().strip().split('\t')

                    except:

                        self.cabecalho = ['x', 'sigma_x', 'y', 'sigma_y']

            except Exception as e:

                # Error handling is already done in read_file method

                pass



    def update_scales(self):

        """Update plot scales"""

        if hasattr(self, 'x_scale') and hasattr(self, 'y_scale'):

            if self.x_scale.get() == TRANSLATIONS[self.language]['log']:

                self.ax.set_xscale('log')

            else:

                self.ax.set_xscale('linear')

            

            if self.y_scale.get() == TRANSLATIONS[self.language]['log']:

                self.ax.set_yscale('log')

            else:

                self.ax.set_yscale('linear')

            self.canvas.draw()



    def apply_preset_model(self, event=None):

        """Apply selected preset model to equation entry"""

        selected = self.model_selector.get()

        if selected in self.preset_models:

            equation = self.preset_models[selected]

            self.equation_entry.delete(0, tk.END)

            self.equation_entry.insert(0, equation)

            self.update_estimates_frame()

            

    def validate_equation(self, event=None):

        """Validate equation in real-time"""

        equation = self.equation_entry.get().replace('^', '**')

        try:

            if '=' in equation:

                equation = equation.split('=')[1].strip()

            sp.sympify(equation)

            self.equation_entry.configure(foreground="black")

            return True

        except:

            self.equation_entry.configure(foreground="red")

            return False

            

    def export_results(self):

        """Export fit results to file"""

        if not hasattr(self, 'last_result'):

            messagebox.showwarning("Aviso", "Nenhum ajuste para exportar.")

            return

            

        filename = filedialog.asksaveasfilename(

            title="Exportar Resultados",

            filetypes=[("CSV", "*.csv"), ("JSON", "*.json"), ("Texto", "*.txt")]

        )

        if not filename:

            return

            

        try:

            if filename.endswith('.json'):

                self.export_json(filename)

            elif filename.endswith('.csv'):

                self.export_csv(filename)

            else:

                self.export_txt(filename)

            messagebox.showinfo("Sucesso", f"Resultados exportados para {filename}")

        except Exception as e:

            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

            

    def export_json(self, filename):

        """Export results to JSON format"""

        data = {

            'equation': self.equacao,

            'parameters': {str(p): {'value': float(v), 'error': float(e)} 

                          for p, v, e in zip(self.parametros, self.last_result.beta, self.last_result.sd_beta)},

            'statistics': {

                'chi_squared': float(self.last_chi2),

                'reduced_chi_squared': float(self.last_result.res_var),

                'r_squared': float(self.last_r2)

            }

        }

        with open(filename, 'w') as f:

            json.dump(data, f, indent=2)

            

    def export_csv(self, filename):

        """Export results to CSV format"""

        df = pd.DataFrame({

            'Parameter': [str(p) for p in self.parametros],

            'Value': self.last_result.beta,

            'Error': self.last_result.sd_beta

        })

        df.to_csv(filename, index=False)

        

    def export_txt(self, filename):

        """Export results to text format"""

        with open(filename, 'w') as f:

            f.write(self.results_text.get(1.0, tk.END))

            

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

            self.last_result = fit_data['result']

            self.last_chi2 = fit_data['chi2']

            self.last_r2 = fit_data['r2']

            self.mostrar_resultados(self.last_result)

            self.update_history_label()

            

    def update_history_label(self):

        """Update history navigation label"""

        total = len(self.history)

        current = self.history_index + 1 if total > 0 else 0

        self.history_label.config(text=f"Histórico: {current}/{total}")

        

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

        """Read data from file"""

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

            # Check file extension and read accordingly

            _, ext = os.path.splitext(file_name)

            ext = ext.lower()

            

            if ext in ['.xlsx', '.xls']:

                # Excel file support

                df = pd.read_excel(file_name)

                if len(df.columns) < 4:

                    raise ValueError("Excel deve ter pelo menos 4 colunas: x, sigma_x, y, sigma_y")

                x = df.iloc[:, 0].values.astype(float)

                sigma_x = df.iloc[:, 1].values.astype(float)

                y = df.iloc[:, 2].values.astype(float) 

                sigma_y = df.iloc[:, 3].values.astype(float)

                self.update_data_preview(df)

                return x, sigma_x, y, sigma_y

                

            elif ext == '.json':

                # JSON file support

                with open(file_name, 'r') as f:

                    data = json.load(f)

                x = np.array(data['x'], dtype=float)

                sigma_x = np.array(data['sigma_x'], dtype=float)

                y = np.array(data['y'], dtype=float)

                sigma_y = np.array(data['sigma_y'], dtype=float)

                preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})

                self.update_data_preview(preview_data)

                return x, sigma_x, y, sigma_y

            

            else:

                # Text/CSV file processing (original logic)

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



                # Check number of columns

                for i, line in enumerate(lines):

                    parts = line.strip().split(delimiter)

                    if len(parts) != 4:

                        messagebox.showerror("Erro ao ler arquivo",

                            f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")

                        raise ValueError(f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")

                

                # Load data using numpy

                dados = np.genfromtxt(file_name, delimiter=delimiter, skip_header=1, dtype=str)

                dados = np.char.replace(dados, ',', '.')

                x = dados[:, 0].astype(float)

                sigma_x = dados[:, 1].astype(float)

                y = dados[:, 2].astype(float)

                sigma_y = dados[:, 3].astype(float)

                

                # Update preview

                preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})

                self.update_data_preview(preview_data)

                return x, sigma_x, y, sigma_y

                

        except Exception as e:

            messagebox.showerror(

                TRANSLATIONS[self.language]['error'],

                error_messages['processing_error'][self.language].format(error=str(e))

            )

            raise

              

    def create_model(self, equation, parameters):

        """Create numerical model with caching"""

        # Check cache first  

        cache_key = f"{equation}-{'-'.join(str(p) for p in parameters)}"

        if cache_key in self.model_cache:

            return self.model_cache[cache_key]

            

        x = sp.Symbol('x')

        expr = sp.sympify(equation)

        

        derivadas = [sp.diff(expr, p) for p in parameters]

        

        modelo_numerico = sp.lambdify((parameters, x), expr, 'numpy')

        derivadas_numericas = [sp.lambdify((parameters, x), d, 'numpy') for d in derivadas]

        

        # Cache the result

        self.model_cache[cache_key] = (modelo_numerico, derivadas_numericas)

        return modelo_numerico, derivadas_numericas

    

    def perform_fit(self):

        """Perform curve fitting"""

        try:

            num_points = int(self.num_points_entry.get())

            if num_points <= 0:

                raise ValueError(TRANSLATIONS[self.language]['positive_points'])

        except ValueError:

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

        """Display fitting results"""

        try:

            # Calcular estatísticas

            if self.modelo is None:

                raise RuntimeError("Model function is not initialized.")

            y_pred = self.modelo(resultado.beta, self.x)

            chi2_total = np.sum(((self.y - y_pred) / self.sigma_y) ** 2)

            r2 = 1 - np.sum((self.y - y_pred) ** 2) / np.sum((self.y - np.mean(self.y)) ** 2)

            

            # Store results for export and history

            self.last_result = resultado

            self.last_chi2 = chi2_total

            self.last_r2 = r2

            

            # Add to history

            fit_data = {

                'result': resultado,

                'chi2': chi2_total,

                'r2': r2,

                'equation': self.equacao,

                'parameters': self.parametros

            }

            self.history.append(fit_data)

            self.history_index = len(self.history) - 1

            self.update_history_label()

            

            # Mostrar resultados

            self.results_text.delete(1.0, tk.END)

            self.results_text.insert(tk.END, f"=== {TRANSLATIONS[self.language]['results']} ===\n")

            for p, v, e in zip(self.parametros, resultado.beta, resultado.sd_beta):

                self.results_text.insert(tk.END, f"{p} = {v:.6f} ± {e:.6f}\n")

            self.results_text.insert(tk.END, f"\n{TRANSLATIONS[self.language]['chi_squared']}: {chi2_total:.2f}\n")

            self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['reduced_chi_squared']}: {resultado.res_var:.2f}\n")

            self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['r_squared']}: {r2:.4f}\n")

            

            # Atualizar gráfico principal

            self.ax.clear()

            self.ax.errorbar(self.x, self.y, xerr=self.sigma_x, yerr=self.sigma_y, fmt='o', label=TRANSLATIONS[self.language]['data_points'])

            num_points = int(self.num_points_entry.get())

            x_fit = np.linspace(min(self.x), max(self.x), num_points)

            self.ax.plot(x_fit, self.modelo(resultado.beta, x_fit), 'r-', label=TRANSLATIONS[self.language]['fit_curve'])

            

            # Atualizar gráfico de resíduos

            self.ax_res.clear()

            residuals = self.y - y_pred

            self.ax_res.scatter(self.x, residuals, color='green', marker='x', label='Resíduos')

            self.ax_res.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

            self.ax_res.set_xlabel(self.x_label_var.get())

            self.ax_res.set_ylabel('Resíduos')

            self.ax_res.grid(True, alpha=0.3)

            

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

            

            # Adjust layout and draw

            self.fig.tight_layout()

            self.canvas.draw()

            

        except Exception as e:

            messagebox.showerror(TRANSLATIONS[self.language]['error'], f"Erro ao mostrar resultados: {str(e)}")