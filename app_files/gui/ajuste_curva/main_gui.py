"""Main GUI class for curve fitting"""
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import List, Optional, Callable, Union, Any, cast, Dict, Tuple, Sequence # Added Sequence
import numpy as np
import numpy.typing as npt
import pandas as pd
from pandas import DataFrame as PandasDataFrame # Added for type alias
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt


from app_files.utils.constants import TRANSLATIONS
from app_files.gui.ajuste_curva.data_handler import read_file # type: ignore[reportUnknownVariableType]

from app_files.gui.ajuste_curva.model_manager import ModelManager
from app_files.gui.ajuste_curva.plot_manager import PlotManager
from app_files.gui.ajuste_curva.adjustment_points_manager import AdjustmentPointsManager
from app_files.gui.ajuste_curva.parameter_estimates_manager import ParameterEstimatesManager
from app_files.gui.ajuste_curva.custom_function_manager import CustomFunctionManager
from app_files.gui.ajuste_curva.advanced_config_dialog import AdvancedConfigDialog
from app_files.gui.ajuste_curva.history_manager import HistoryManager
from app_files.gui.ajuste_curva.ui_builder import UIBuilder
from app_files.gui.ajuste_curva.graph_export_manager import GraphExportManager
from app_files.gui.ajuste_curva.data_export_manager import DataExportManager

# Type aliases for clarity
FloatArray = npt.NDArray[np.float64]
# Adjusted ModelFunction to match ModelCallable from model_manager.py
ModelFunction = Callable[[Sequence[float], FloatArray], FloatArray]
DerivFunction = Callable[[Sequence[float], FloatArray], FloatArray] # Adjusted to match ModelCallable style
ReadFileReturnType = Tuple[FloatArray, FloatArray, FloatArray, FloatArray, PandasDataFrame]
# Corrected CreateModelReturnType: List[DerivFunction] is not Optional
CreateModelReturnType = Tuple[Optional[ModelFunction], List[DerivFunction]]

class AjusteCurvaFrame(tk.Frame):  # Changed to inherit from tk.Frame
    """GUI class for curve fitting"""

    def __init__(self, parent: Union[tk.Tk, tk.Toplevel, tk.Widget], language: str = 'pt') -> None:
        """Initialize the GUI

        Args:
            parent: Parent widget (window or frame)
            language: Interface language (default: 'pt')
        """
        
        super().__init__(parent)  # Call the parent constructor
        self.parent = parent # Storing the Tk parent widget
        self.language: str = language
            
            # Only set title if parent is a window
        if isinstance(parent, (tk.Tk, tk.Toplevel)):
            parent.title(TRANSLATIONS[self.language]['curve_fitting_title'])

        # Initialize instance variables for data (these don't depend on managers or UI)
        self.x: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.y: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.sigma_x: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.sigma_y: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.cabecalho: List[str] = []
        self.modelo: Optional[ModelFunction] = None

        # Initialize managers that UIBuilder's setup_ui() might depend on
        self.model_manager = ModelManager()
        self.history_manager = HistoryManager(self, language)
        # ParameterEstimatesManager is used by update_estimates_frame, which is bound in UIBuilder
        self.parameter_estimates_manager = None

        # Initialize UIBuilder and setup the UI framework
        self.ui_builder: UIBuilder = UIBuilder(self, language)
        self.ui_builder.setup_ui()

        # Setup matplotlib components (creates figure, axes, canvas and PlotManager)
        self._setup_plot_area()

        # Initialize other managers that depend on the canvas or fully constructed UI
        self.adjustment_points_manager = AdjustmentPointsManager(self, language)
        self.custom_function_manager = CustomFunctionManager(self, self.ax, self.canvas, language)
        self.graph_export_manager = GraphExportManager(self, language)
        self.data_export_manager = DataExportManager(self, language)

        # Ensure this is initialized before advanced_config_dialog
        from .parameter_estimates_manager import ParameterEstimatesManager
        self.parameter_estimates_manager = ParameterEstimatesManager(self, self.language)

        # Then initialize advanced_config_dialog with the parameter_estimates_manager
        self.advanced_config_dialog = AdvancedConfigDialog(
            self,
            self.custom_function_manager,
            self.parameter_estimates_manager,
            self.adjustment_points_manager,
            self.language
        )

        # Model and fitting variables
        self.equacao = ""
        self.parametros: List[sp.Symbol] = []
        self.odr = None
        # Last results
        self.last_result: Any = None
        self.last_chi2: float = 0.0
        self.last_r2: float = 0.0
        # Additional attributes to avoid pylint warnings
        self.custom_functions: Dict[str, Any] = {}
        self.adjustment_points_selection_mode: str = 'Todos'
        self.selected_adjustment_points: List[int] = []
        self.selected_point_indices: List[int] = []
        self.estimates_frame: Optional[tk.Widget] = None

        # Configure the AjusteCurvaFrame itself to allow its content to expand
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Initialize empty plot after a short delay
        self.parent.after(100, self.plot_manager.initialize_empty_plot)    

        
    def _setup_plot_area(self) -> None:
        """Create or recreate the plot area with canvas"""
        # Close existing figure if any
        if hasattr(self, 'fig') and self.fig:
            plt.close(self.fig)
        
        # Use Any to avoid complex type issues with matplotlib
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))  # type: ignore
        self.fig = fig
        # Matplotlib returns either a single Axes or an array of Axes depending on inputs
        # For 2x1 subplots with default squeeze=True, it returns an array
        # Use Any to bypass type checking complications
        self.ax: Any = axes[0] if hasattr(axes, '__len__') else axes
        self.ax_res: Any = axes[1] if hasattr(axes, '__len__') else None
        
        # Create new canvas
        if self.ui_builder.plot_area_frame is None:
            raise RuntimeError("UIBuilder did not create the plot_area_frame.")
            
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.ui_builder.plot_area_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(highlightthickness=0)
        canvas_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Initialize plot manager with new canvas
        self.plot_manager = PlotManager(self.fig, self.ax, self.ax_res, self.canvas, self.language)
        

    # Forward UI element access to the UI builder with more concise implementation
    def _get_ui_attr(self, attr_name: str) -> Any:
        """Helper method to safely get UI attributes"""
        return getattr(self.ui_builder, attr_name) if hasattr(self, 'ui_builder') and self.ui_builder and hasattr(self.ui_builder, attr_name) else None

    # UI property getters - All use _get_ui_attr for consistent access pattern
    @property
    def data_text(self) -> Optional[tk.Text]:
        return self._get_ui_attr('data_text')

    @property
    def results_text(self) -> Optional[tk.Text]:
        return self._get_ui_attr('results_text')

    @property
    def title_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr('title_entry')

    @property
    def x_label_var(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr('x_label_var')

    @property
    def y_label_var(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr('y_label_var')

    @property
    def x_scale(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr('x_scale')

    @property
    def y_scale(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr('y_scale')

    @property
    def file_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr('file_entry')

    @property
    def equation_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr('equation_entry')

    @property
    def model_selector(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr('model_selector')

    @property
    def num_points_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr('num_points_entry')

    @property
    def max_iter_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr('max_iter_entry')

    @property
    def progress_var(self) -> Optional[tk.IntVar]:
        return self._get_ui_attr('progress_var')

    @property
    def status_label(self) -> Optional[tk.Label]:
        return self._get_ui_attr('status_label')

    @property
    def save_graph_option(self) -> Optional[tk.StringVar]: # Changed from tk.BooleanVar
        return self._get_ui_attr('save_graph_option')

    def update_data_preview(self, data: pd.DataFrame) -> None:
        """Update data preview text widget - showing all data"""
        if self.data_text:
            self.data_text.delete(1.0, tk.END)
            preview_str = data.to_string(index=False, float_format='%.4f') # type: ignore[reportUnknownVariableType]
            self.data_text.insert(1.0, preview_str)
            # Update plot with data immediately
            self.plot_data_only()

    def plot_data_only(self):
        """Plot only the data points without any curve fitting"""
        if len(self.x) == 0 or len(self.y) == 0:
            return

        # Get scales and labels with fallbacks
        x_scale = 'log' if self.x_scale and self.x_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
        y_scale = 'log' if self.y_scale and self.y_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
        x_label = self.x_label_var.get() if self.x_label_var else "X"
        y_label = self.y_label_var.get() if self.y_label_var else "Y"
        title = self.title_entry.get() if self.title_entry else ""

        self.plot_manager.plot_data_only( # type: ignore[reportUnknownMemberType]
            self.x, self.y, self.sigma_x, self.sigma_y,
            x_label=x_label,
            y_label=y_label,
            title=title,
            x_scale=x_scale,
            y_scale=y_scale
        )

    def browse_file(self):
        """Open file dialog to select data file"""

        filename = filedialog.askopenfilename(
            title=TRANSLATIONS[self.language]['select_data_file'],
            filetypes=[
                ("Todos os compatÃ­veis", "*.xlsx;*.xls;*.txt;*.csv;*.json"),
                ("Excel files", "*.xlsx *.xls"),
                ("Text or CSV files", "*.txt *.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if filename and self.file_entry:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            # Automatically load data when file is selected
            try:
                data_tuple = read_file(filename, self.language) # type: ignore[reportUnknownVariableType]
                # No cast needed if read_file has proper return type annotation and Pylance infers it
                self.x, self.sigma_x, self.y, self.sigma_y, df = data_tuple

                self.update_data_preview(df)
                with open(filename, 'r', encoding='utf-8') as f:
                    try:
                        self.cabecalho = f.readline().strip().split('\t')
                    except (UnicodeDecodeError, AttributeError, ValueError):
                        self.cabecalho = ['x', 'sigma_x', 'y', 'sigma_y']

                # Plotar dados imediatamente após carregar
                self.parent.after(100, self.plot_data_only)
                  # Update graph appearance after loading data
                self.update_graph_appearance() # type: ignore[reportUnknownVariableType]

            except (FileNotFoundError, PermissionError, IOError, ValueError, TypeError):
                # Error handling is already done in read_file method
                pass

    def update_scales(self):
        """Update plot scales based on user selection"""
        """Update plot scales and redraw plot"""
        if len(self.x) == 0 or len(self.y) == 0 or not self.x_scale or not self.y_scale:
            return

        # Get and apply scales
        x_scale = 'log' if self.x_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
        y_scale = 'log' if self.y_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'

        self.plot_manager.ax.set_xscale(x_scale) # type: ignore[reportUnknownVariableType]
        self.plot_manager.ax.set_yscale(y_scale) # type: ignore[reportUnknownVariableType]
        self.plot_manager.ax_res.set_xscale(x_scale) # type: ignore[reportUnknownVariableType]

        # Force canvas update
        self.plot_manager.fig.tight_layout() # type: ignore[reportUnknownVariableType]
        self.plot_manager.canvas.draw() # type: ignore[reportUnknownVariableType]
          # If we have a fit model, redraw everything
        if hasattr(self, 'last_result') and self.last_result is not None:
            self.plot_data_only()
        else:
            # Otherwise just update the plot with data only
            self.plot_data_only()

    def apply_preset_model(self, _event: Optional[tk.Event] = None) -> None: # type: ignore[reportGeneralTypeIssues]
        """Apply selected preset model to equation entry

        Args:
            _event: Event parameter required by tkinter combobox binding but not used
        """
        if not self.model_selector or not self.equation_entry:
            return

        selected = self.model_selector.get()
        if selected in self.model_manager.preset_models:
            equation = self.model_manager.preset_models[selected]
            self.equation_entry.delete(0, tk.END)
            self.equation_entry.insert(0, equation)
            self.update_estimates_frame()
    def validate_equation(self, _event: Optional[Any] = None) -> bool: # Changed _event type hint
        """Validate equation in real-time

        Args:
            _event: Event parameter required by tkinter binding but not used

        Returns:
            bool: True if equation is valid, False otherwise
        """
        if not self.equation_entry:
            return False

        equation = self.equation_entry.get().replace('^', '**')
        try:
            if '=' in equation:
                equation = equation.split('=')[1].strip()

            sp.sympify(equation, locals={"exp": sp.exp, "log": sp.log, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "pi": sp.pi}) # type: ignore[reportUnknownVariableType]
            self.equation_entry.configure(foreground="black")
            return True
        except (ValueError, TypeError, SyntaxError):
            self.equation_entry.configure(foreground="red")
            return False

    def update_estimates_frame(self):
        """Update the parameter estimates frame based on current equation"""
        """Update the estimates frame based on the equation"""
        if not self.equation_entry:
            return

        equation = self.equation_entry.get()
        if equation:
            self.parameter_estimates_manager.update_estimates_frame(equation) # type: ignore[reportUnknownVariableType]
            # Update parametros for compatibility with other parts of the code
            self.parametros = self.parameter_estimates_manager.parameters # type: ignore[reportUnknownVariableType]

    def export_results(self):
        """Export fitting results to file"""
        """Export fit results to file"""
        self.data_export_manager.export_results()

    def save_graph(self):
        """Save the current graph to file"""
        """Save graph to file"""
        self.graph_export_manager.save_graph()

    def perform_fit(self):
        """Perform the curve fitting operation"""
        """Perform curve fitting"""
        if not self.num_points_entry:
            messagebox.showerror(TRANSLATIONS[self.language]['error'],  # type: ignore[misc]
                                TRANSLATIONS[self.language]['invalid_points'])
            return

        try:
            num_points = int(self.num_points_entry.get())
            if num_points <= 0:
                raise ValueError(TRANSLATIONS[self.language]['positive_points'])
        except ValueError:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], TRANSLATIONS[self.language]['invalid_points'])  # type: ignore[misc]
            return

        try:
            # Reset progress and status
            if self.progress_var:
                self.progress_var.set(0)
            if self.status_label:
                self.status_label.config(text=TRANSLATIONS[self.language]['starting_fit'])
            self.parent.update()

            # Clear previous results
            if self.results_text:
                self.results_text.delete(1.0, tk.END)

            # Update estimates if needed
            if not self.parametros:
                self.update_estimates_frame()

            # Get field values
            if not self.file_entry or not self.equation_entry or not self.max_iter_entry:
                messagebox.showerror(TRANSLATIONS[self.language]['error'],  # type: ignore[misc]
                                    "UI elements not initialized properly")
                return

            caminho = self.file_entry.get()
            equacao = self.equation_entry.get().replace('^', '**')
            if '=' in equacao:
                equacao = equacao.split('=')[1].strip()
            max_iter = int(self.max_iter_entry.get())

            # Get initial estimates from parameter manager
            chute = self.parameter_estimates_manager.get_initial_estimates() # type: ignore[reportUnknownMemberType]
            # No cast needed if get_initial_estimates has proper return type annotation

            # Load data
            data_tuple = read_file(caminho, self.language) # type: ignore[reportUnknownVariableType]
            # No cast needed if read_file has proper return type annotation
            self.x, self.sigma_x, self.y, self.sigma_y, _ = data_tuple

            with open(caminho, 'r', encoding='utf-8') as f:
                self.cabecalho = f.readline().strip().split('\\\\t')

            # Create model
            model_result_tuple = self.model_manager.create_model(equacao, self.parametros) # type: ignore[reportUnknownMemberType]
            # Cast is appropriate here if Pylance cannot infer the precise tuple structure from create_model
            typed_model_result = cast(CreateModelReturnType, model_result_tuple)
            self.modelo, derivadas = typed_model_result

            if self.modelo is None:
                raise RuntimeError("Model function is not initialized.")

            # Store equation for later use
            self.equacao = equacao

            def run_odr():
                try:
                    # Use cast to ensure self.modelo is not None when passed to perform_odr_fit
                    modelo_not_none = cast(ModelFunction, self.modelo)
                    # Corrected parameter names for perform_odr_fit
                    resultado, chi2_total, r2 = self.model_manager.perform_odr_fit( # type: ignore[reportUnknownVariableType]
                        x=self.x, y=self.y,
                        sigma_x=self.sigma_x, sigma_y=self.sigma_y,
                        model_func=modelo_not_none, # Corrected name
                        derivs=derivadas,          # Corrected name
                        initial_params=chute,      # Corrected name
                        max_iter=max_iter
                    )

                    # Store results
                    self.last_result = resultado
                    self.last_chi2 = float(chi2_total) # chi2_total should be float from perform_odr_fit
                    self.last_r2 = float(r2)         # r2 should be float from perform_odr_fit

                    # Add to history
                    self.history_manager.add_fit_result( # type: ignore[reportUnknownMemberType]
                        resultado, chi2_total, r2, self.equacao, self.parametros
                    )

                    # Update UI
                    self.parent.after(0, lambda: self.mostrar_resultados(resultado))
                    if self.status_label:
                        status_label = self.status_label  # Local reference to avoid closure issues
                        self.parent.after(0, lambda: status_label.config(
                            text=TRANSLATIONS[self.language]['fit_complete']) if status_label else None)

                except (ValueError, TypeError, AttributeError, RuntimeError, ZeroDivisionError) as e:
                    self.parent.after(0, lambda: messagebox.showerror(  # type: ignore[misc]
                        TRANSLATIONS[self.language]['error'],
                        f"{TRANSLATIONS[self.language]['fit_error']}: {str(e)}"
                    ))
                    if self.status_label:
                        status_label = self.status_label  # Local reference to avoid closure issues
                        self.parent.after(0, lambda: status_label.config(
                            text=TRANSLATIONS[self.language]['fit_error'])
                            if status_label else None)
            def update_progress():
                if hasattr(self, 'odr') and self.odr is not None and hasattr(self.odr, 'iwork') and self.odr.iwork is not None:
                    try:
                        current_iter = self.odr.iwork[0]
                        if self.progress_var:
                            self.progress_var.set(min(100, current_iter * 10))
                        if self.status_label:
                            status_label = self.status_label  # Local reference for thread safety
                            status_label.config(text=f"IteraÃ§Ã£o: {current_iter}")
                        if current_iter < max_iter:
                            self.parent.after(100, update_progress)
                    except (AttributeError, IndexError, TypeError):
                        self.parent.after(100, update_progress)
                else:
                    self.parent.after(100, update_progress)

            # Start progress updates
            self.parent.after(100, update_progress)
              # Start ODR in separate thread
            threading.Thread(target=run_odr, daemon=True).start()

        except (FileNotFoundError, PermissionError, ValueError, TypeError, AttributeError) as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], f"{TRANSLATIONS[self.language]['fit_error']}: {str(e)}")  # type: ignore[misc]
            if self.results_text:
                self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['verify_and_retry']}\\n")

    def mostrar_resultados(self, resultado: Any):  # Added type hint for 'resultado'
        """Display fitting results in the interface

        Args:
            resultado: The fitting result object
        """
        """Display fitting results"""
        try:
            # Check if model is initialized
            if self.modelo is None:
                raise RuntimeError("Model function is not initialized.")

            # Display results in text widget
            if not self.results_text:
                return

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"=== {TRANSLATIONS[self.language]['results']} ===\n")
            for p, v, e in zip(self.parametros, resultado.beta, resultado.sd_beta):
                self.results_text.insert(tk.END, f"{p} = {v:.6f}  {e:.6f}\n")

            self.results_text.insert(tk.END, f"\n{TRANSLATIONS[self.language]['chi_squared']}: {self.last_chi2:.2f}\n")
            self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['reduced_chi_squared']}: {resultado.res_var:.2f}\n")
            self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['r_squared']}: {self.last_r2:.4f}\n")

            # Get scales with fallbacks
            x_scale = 'log' if self.x_scale and self.x_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
            y_scale = 'log' if self.y_scale and self.y_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'

            # Get plot labels safely
            x_label = self.x_label_var.get() if self.x_label_var else "X"
            y_label = self.y_label_var.get() if self.y_label_var else "Y"
            title = self.title_entry.get() if self.title_entry else ""

            # Plot results
            num_points = int(self.num_points_entry.get()) if self.num_points_entry else 1000
            self.plot_manager.plot_fit_results( # type: ignore[reportUnknownMemberType]
                self.x, self.y, self.sigma_x, self.sigma_y,
                self.modelo, resultado, self.last_chi2, self.last_r2, # Removed unnecessary cast
                self.equacao, self.parametros, num_points,
                x_label=x_label,
                y_label=y_label,
                title=title,
                x_scale=x_scale,
                y_scale=y_scale            )
            # If we have custom functions, update them to show on the plot
            if hasattr(self.custom_function_manager, 'custom_functions') and self.custom_function_manager.custom_functions:
                self.custom_function_manager.update_plot()

        except (AttributeError, ValueError, TypeError, RuntimeError) as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], f"Erro ao mostrar resultados: {str(e)}")  # type: ignore[misc]

    def update_graph_appearance(self, _event: Optional[tk.Event] = None): # type: ignore[reportGeneralTypeIssues]
        """Update graph title, labels and aspect ratio

        Args:
            _event: Event parameter required by tkinter binding but not used
        """
        # Update title and labels (with safe access)
        title = self.title_entry.get() if self.title_entry else None
        x_label = self.x_label_var.get() if self.x_label_var else None
        y_label = self.y_label_var.get() if self.y_label_var else None

        # Get axis scales (with safe access)
        x_scale = 'log' if (self.x_scale and self.x_scale.get() == TRANSLATIONS[self.language]['log']) else 'linear'
        y_scale = 'log' if (self.y_scale and self.y_scale.get() == TRANSLATIONS[self.language]['log']) else 'linear'

        # Use plot manager to update appearance
        self.plot_manager.update_graph_appearance( # type: ignore[reportUnknownMemberType]
            title=title,
            x_label=x_label,
            y_label=y_label
        )
          # Also update the scales
        self.plot_manager.ax.set_xscale(x_scale) # type: ignore[reportUnknownVariableType]
        self.plot_manager.ax.set_yscale(y_scale) # type: ignore[reportUnknownVariableType]
        self.plot_manager.fig.tight_layout() # type: ignore[reportUnknownVariableType]
        self.plot_manager.canvas.draw() # type: ignore[reportUnknownVariableType]

    def switch_language(self, language: str):  # Added type hint for language
        """Switch the interface language

        Args:
            language: The new language code ('pt' or 'en')
        """
        """Update language for this component"""
        self.language = language
        # Update languages for all managers
        self.adjustment_points_manager.language = language
        self.custom_function_manager.language = language
        self.history_manager.language = language
        self.graph_export_manager.language = language
        self.data_export_manager.language = language
        self.plot_manager.set_language(language) 

        if self.parameter_estimates_manager is None:
            self.parameter_estimates_manager = ParameterEstimatesManager(self, language)
        else:
            self.parameter_estimates_manager.language = language
            self.parameter_estimates_manager.parent = self

        # Store current state
        current_data = ""
        current_equation = ""
        current_title = ""
        current_x_label = ""
        current_y_label = ""
        current_x_scale = "linear"
        current_y_scale = "linear"

        if hasattr(self, 'ui_builder') and self.ui_builder:
            # Save current values
            if self.data_text:
                current_data = self.data_text.get(1.0, tk.END)
            if self.equation_entry:
                current_equation = self.equation_entry.get()
            if self.title_entry:
                current_title = self.title_entry.get()
            if self.x_label_var:
                current_x_label = self.x_label_var.get()
            if self.y_label_var:
                current_y_label = self.y_label_var.get()
            if self.x_scale:
                current_x_scale = 'log' if self.x_scale.get() == TRANSLATIONS['pt']['log'] or self.x_scale.get() == TRANSLATIONS['en']['log'] else 'linear'
            if self.y_scale:
                current_y_scale = 'log' if self.y_scale.get() == TRANSLATIONS['pt']['log'] or self.y_scale.get() == TRANSLATIONS['en']['log'] else 'linear'

            # Clear and rebuild UI
            for widget in self.winfo_children():  # Changed from self.parent.winfo_children()
                widget.destroy()
                
            self.ui_builder.language = language
            self.ui_builder.setup_ui()

            # RECREATE plot area and canvas
            self._setup_plot_area()
            
            # REINITIALIZE managers that depend on the UI
            self.adjustment_points_manager = AdjustmentPointsManager(self, language)
            self.custom_function_manager = CustomFunctionManager(self, self.ax, self.canvas, language)
            self.graph_export_manager = GraphExportManager(self, language)
            self.data_export_manager = DataExportManager(self, language)
            
            # Recreate advanced config dialog
            self.advanced_config_dialog = AdvancedConfigDialog(
            self, 
            self.custom_function_manager,
            self.parameter_estimates_manager,
            self.adjustment_points_manager,  # Add this parameter
            self.language
            )
            
            # Update custom function manager references
            self.custom_function_manager.ax = self.ax
            self.custom_function_manager.canvas = self.canvas
            
            # Restore values
            if self.data_text and current_data.strip():
                self.data_text.insert(1.0, current_data)
            if self.equation_entry:
                self.equation_entry.insert(0, current_equation)
            if self.title_entry:
                self.title_entry.insert(0, current_title)
            if self.x_label_var:
                self.x_label_var.set(current_x_label)
            if self.y_label_var:
                self.y_label_var.set(current_y_label)
            if self.x_scale:
                self.x_scale.set(TRANSLATIONS[self.language][current_x_scale])
            if self.y_scale:
                self.y_scale.set(TRANSLATIONS[self.language][current_y_scale])# Update plot appearance with new language
        if hasattr(self, 'plot_manager') and self.plot_manager:
            # If we have data, replot it to ensure the plot is visible with new language
            if hasattr(self, 'x') and len(self.x) > 0:
                # Check if we have fit results to replot
                if hasattr(self, 'last_result') and self.last_result is not None:
                    # Re-run the display results method to recreate the plot with new language
                    self.mostrar_resultados(self.last_result)
                else:
                    # Just replot the data
                    self.plot_data_only()
            else:
                # No data, just refresh labels on empty plot
                self.plot_manager.refresh_current_plot() # type: ignore[reportUnknownVariableType]

            self.update_graph_appearance() # type: ignore[reportUnknownVariableType]

    def cleanup(self):
        """Clean up resources when closing the interface"""
        """Clean up resources when tab is closed"""
        # Close matplotlib figure to prevent memory leaks
        if hasattr(self, 'fig') and self.fig:
            plt.close(self.fig)

        # Clear data arrays
        if hasattr(self, 'x'):
            self.x = np.array([])
        if hasattr(self, 'y'):
            self.y = np.array([])
        if hasattr(self, 'sigma_x'):
            self.sigma_x = np.array([])
        if hasattr(self, 'sigma_y'):
            self.sigma_y = np.array([])

        # Clear model references
        self.modelo = None
        self.odr = None

    def on_tab_activated(self):
        """Handle tab activation event"""
        """Called when this tab becomes active"""
        # Redraw plots if needed
        if hasattr(self, 'plot_manager') and self.plot_manager:
            if hasattr(self.plot_manager, 'canvas'):
                self.plot_manager.canvas.draw()

    def show_advanced_config(self):
        """Show the advanced configuration dialog"""
        """Show advanced configuration dialog"""
        self.advanced_config_dialog.show_dialog()

    def update_custom_functions(self, custom_functions: Optional[Dict[str, Any]] = None):  # Added type hint for custom_functions
        """Update the custom functions for curve fitting

        Args:
            custom_functions: Dictionary of custom functions
        """
        if custom_functions is not None:
            self.custom_functions = custom_functions

        # Update the UI or refit the curve as needed
        if hasattr(self, 'update_fit_with_current_points'):
            self.update_fit_with_current_points()

    def update_selection_mode(self, selection_mode: str):  # Added type hint for selection_mode
        """Update the selection mode for adjustment points

        Args:
            selection_mode: The selection mode ('Todos', 'Selecionados', or 'Faixa')
        """
        # Store the selection mode
        if not hasattr(self, 'adjustment_points_selection_mode'):
            self.adjustment_points_selection_mode = selection_mode
        else:
            self.adjustment_points_selection_mode = selection_mode

        # Update any UI elements if needed

    def update_adjustment_points(self, selected_indices: List[int]):
        """Update the selected adjustment points

        Args:
            selected_indices: List of indices of selected points
        """        # Store the selected indices
        self.selected_point_indices = selected_indices

    def update_fit_with_current_points(self):
        """Update the fit using currently selected points"""
        if hasattr(self, 'last_result') and self.last_result is not None:
            # Only refit if we already have a previous fit
            self.mostrar_resultados(self.last_result)

