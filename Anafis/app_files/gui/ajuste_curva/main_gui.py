"""Main GUI class for curve fitting"""
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import List, Optional, Callable, Union, Any, cast, Tuple, Sequence # Added Sequence
import numpy as np
import numpy.typing as npt
import pandas as pd
import sympy as sp #type: ignore[import-untyped]
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import logging
from pandas import DataFrame as PandasDataFrame  # type: ignore[import-untyped]


from app_files.utils.constants import TRANSLATIONS
from app_files.gui.ajuste_curva.data_handler import read_file

from app_files.gui.ajuste_curva.model_manager import ModelManager
from app_files.gui.ajuste_curva.plot_manager import PlotManager
from app_files.gui.ajuste_curva.adjustment_points_manager import AdjustmentPointsManager
from app_files.gui.ajuste_curva.custom_function_manager import CustomFunctionManager, CustomFunction
from app_files.gui.ajuste_curva.advanced_config_dialog import AdvancedConfigDialog
from app_files.gui.ajuste_curva.history_manager import HistoryManager
from app_files.gui.ajuste_curva.ui_builder import UIBuilder
from app_files.gui.ajuste_curva.graph_export_manager import GraphExportManager
from app_files.utils.user_preferences import UserPreferencesManager
from app_files.utils.user_preferences import UserPreferencesManager


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
        self.modelo: Optional[ModelFunction] = None        # Initialize managers that UIBuilder's setup_ui() might depend on
        self.user_preferences = UserPreferencesManager()
        self.model_manager = ModelManager(language)
        self.history_manager = HistoryManager(self, language)
        # ParameterEstimatesManager is used by update_estimates_frame, which is bound in UIBuilder
        from .parameter_estimates_manager import ParameterEstimatesManager
        self.parameter_estimates_manager = ParameterEstimatesManager(self, language)

        # Initialize UIBuilder and setup the UI framework
        self.ui_builder: UIBuilder = UIBuilder(self, language)
        self.ui_builder.setup_ui()

        # Setup matplotlib components (creates figure, axes, canvas and PlotManager)
        self._setup_plot_area()        # Initialize other managers that depend on the canvas or fully constructed UI
        self.adjustment_points_manager = AdjustmentPointsManager(self, language)
        self.custom_function_manager = CustomFunctionManager(
            self, self.plot_manager, self.user_preferences
        )
        self.graph_export_manager = GraphExportManager(self, language)

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
        self.last_r2: float = 0.0        # Additional attributes to avoid pylint warnings
        self.custom_functions: List[CustomFunction] = []
        self.adjustment_points_selection_mode: str = TRANSLATIONS[self.language]['all_points_value']
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
        
        # Configure matplotlib to suppress icon warnings
        import matplotlib as mpl
        mpl.rcParams['figure.max_open_warning'] = 0  # Suppress too many figures warning
        
        # Ensure we're in the main thread for GUI operations
        import threading
        if threading.current_thread() != threading.main_thread():
            logging.warning("Plot creation called from non-main thread")
            # Schedule plot creation in main thread
            self.after_idle(self._setup_plot_area)
            return
          # Use Any to avoid complex type issues with matplotlib
        # Create subplots with height ratios: main plot gets 4x more space than residuals
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [4, 1]})  # type: ignore
        self.fig = fig
        
        # Set icon handling to avoid conflicts
        fig.canvas.manager.set_window_title("AnaFis - Curve Fitting")  # type: ignore
        
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
            self.data_text.insert(1.0, preview_str)            # Update plot with data immediately
            self.plot_data_only()

    def plot_data_only(self):
        """Plot only the data points without any curve fitting"""
        try:
            logging.info("plot_data_only called")
            
            if len(self.x) == 0 or len(self.y) == 0:
                logging.warning("No data available to plot (empty arrays)")
                return

            # Get scales and labels with fallbacks
            x_scale = 'log' if self.x_scale and self.x_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
            y_scale = 'log' if self.y_scale and self.y_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
            x_label = self.x_label_var.get() if self.x_label_var else "X"
            y_label = self.y_label_var.get() if self.y_label_var else "Y"
            title = self.title_entry.get() if self.title_entry else ""

            logging.info(f"Plotting data: {len(self.x)} points, x_scale={x_scale}, y_scale={y_scale}")

            self.plot_manager.plot_data_only( # type: ignore[reportUnknownMemberType]
                self.x, self.y, self.sigma_x, self.sigma_y,
                x_label=x_label,
                y_label=y_label,
                title=title,
                x_scale=x_scale,
                y_scale=y_scale
            )
            
            # Force canvas redraw
            if hasattr(self.plot_manager, 'canvas') and self.plot_manager.canvas:
                self.plot_manager.canvas.draw_idle()
                self.plot_manager.canvas.draw()
                logging.info("plot_data_only completed successfully")
            else:
                logging.error("Canvas not available for plot_data_only")
                
        except Exception as e:
            logging.error(f"Error in plot_data_only: {e}")
            import traceback
            logging.error(f"plot_data_only traceback: {traceback.format_exc()}")

    def browse_file(self):
        """Open file dialog to select data file"""

        filename = filedialog.askopenfilename(
            title=TRANSLATIONS[self.language]['select_data_file'],
            filetypes=[
                (TRANSLATIONS[self.language]['all_compatible'], "*.xlsx;*.xls;*.txt;*.csv;*.json"),
                (TRANSLATIONS[self.language]['excel_files'], "*.xlsx *.xls"),
                (TRANSLATIONS[self.language]['text_csv_files'], "*.txt *.csv"),
                (TRANSLATIONS[self.language]['json_files'], "*.json"),
                (TRANSLATIONS[self.language]['all_files'], "*.*")
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
                        self.cabecalho = ['x', 'sigma_x', 'y', 'sigma_y']                # Plotar dados imediatamente após carregar
                self.parent.after(100, self.plot_data_only)

            except (FileNotFoundError, PermissionError, IOError, ValueError, TypeError) as e:# Log the error for debugging while maintaining user experience
                logging.debug(f"Error loading file: {e}")
                # Error handling is already done in read_file method

    def update_scales(self):
        """Update plot scales based on user selection and redraw plot"""
        if len(self.x) == 0 or len(self.y) == 0 or not self.x_scale or not self.y_scale:
            return

        # Get and apply scales
        x_scale = 'log' if self.x_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
        y_scale = 'log' if self.y_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'

        self.plot_manager.ax.set_xscale(x_scale) # type: ignore[reportUnknownVariableType]
        self.plot_manager.ax.set_yscale(y_scale) # type: ignore[reportUnknownVariableType]
        self.plot_manager.ax_res.set_xscale(x_scale) # type: ignore[reportUnknownVariableType]

        # Force canvas update
        self.plot_manager.fig.tight_layout() # type: ignore[reportUnknownVariableType]        self.plot_manager.canvas.draw() # type: ignore[reportUnknownVariableType]
        
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
            # Use theme-appropriate color for valid equation
            from app_files.utils.theme_manager import theme_manager
            valid_color = theme_manager.get_adaptive_color('text_valid')
            self.equation_entry.configure(foreground=valid_color)
            return True
        except (ValueError, TypeError, SyntaxError):
            # Use theme-appropriate color for error
            from app_files.utils.theme_manager import theme_manager
            error_color = theme_manager.get_adaptive_color('text_error')
            self.equation_entry.configure(foreground=error_color)
            return False

    def update_estimates_frame(self):
        """Update the parameter estimates frame based on current equation"""
        if not self.equation_entry:
            return

        equation = self.equation_entry.get()
        if equation:
            self.parameter_estimates_manager.update_estimates_frame(equation) # type: ignore[reportUnknownVariableType]            # Update parametros for compatibility with other parts of the code
            self.parametros = self.parameter_estimates_manager.parameters # type: ignore[reportUnknownVariableType]

    def save_graph(self):
        """Save the current graph to file"""
        self.graph_export_manager.save_graph()

    def perform_fit(self):
        """Perform the curve fitting operation"""
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
                self.results_text.delete(1.0, tk.END)            # Update estimates if needed
            if not self.parametros:
                self.update_estimates_frame()
                
            # Get field values
            if not self.file_entry or not self.equation_entry or not self.max_iter_entry:
                messagebox.showerror(TRANSLATIONS[self.language]['error'],  # type: ignore[misc]
                                    "UI elements not initialized properly")
                return

            # Type narrowing: assert entries are not None after the check above
            assert self.file_entry is not None
            assert self.equation_entry is not None
            assert self.max_iter_entry is not None

            caminho = self.file_entry.get()
            equacao = self.equation_entry.get().replace('^', '**')
            if '=' in equacao:
                equacao = equacao.split('=')[1].strip()
            max_iter = int(self.max_iter_entry.get())

            # Check if file path is provided
            if not caminho or caminho.strip() == '':
                messagebox.showerror(TRANSLATIONS[self.language]['error'],  # type: ignore[misc]
                                   TRANSLATIONS[self.language]['select_file_first'])
                return

            # Get initial estimates from parameter manager
            chute = self.parameter_estimates_manager.get_initial_estimates() # type: ignore[reportUnknownMemberType]
            # No cast needed if get_initial_estimates has proper return type annotation            # Load data
            data_tuple = read_file(caminho, self.language) # type: ignore[reportUnknownVariableType]
            # No cast needed if read_file has proper return type annotation
            self.x, self.sigma_x, self.y, self.sigma_y, _ = data_tuple

            # Validate loaded data
            if len(self.x) == 0 or len(self.y) == 0:
                messagebox.showerror(TRANSLATIONS[self.language]['error'],  # type: ignore[misc]
                                   "Data file appears to be empty or invalid")
                return
            
            if len(self.x) != len(self.y):
                messagebox.showerror(TRANSLATIONS[self.language]['error'],  # type: ignore[misc]
                                   "X and Y data arrays have different lengths")
                return

            with open(caminho, 'r', encoding='utf-8') as f:
                self.cabecalho = f.readline().strip().split('\\\\t')

            # Create model
            model_result_tuple = self.model_manager.create_model(equacao, self.parametros) # type: ignore[reportUnknownMemberType]
            # Cast is appropriate here if Pylance cannot infer the precise tuple structure from create_model
            typed_model_result = cast(CreateModelReturnType, model_result_tuple)
            self.modelo, derivadas = typed_model_result

            if self.modelo is None:
                raise RuntimeError("Model function is not initialized.")            # Store equation for later use
            self.equacao = equacao

            def run_fitting():
                try:
                    # Get the selected fitting method
                    fitting_method = self.get_selected_fitting_method()                    
                    # Use cast to ensure self.modelo is not None when passed to fitting methods
                    modelo_not_none = cast(ModelFunction, self.modelo)
                    
                    if fitting_method == "least_squares":
                        # Use Least Squares fitting
                        resultado, chi2_total, r2 = self.model_manager.perform_least_squares_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            max_iter=max_iter
                        )
                    elif fitting_method == "robust":
                        # Use Robust fitting (RANSAC/Huber)
                        resultado, chi2_total, r2 = self.model_manager.perform_robust_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            method='ransac',  # Could be made configurable
                            max_iter=max_iter
                        )
                    elif fitting_method == "weighted":
                        # Use Weighted Least Squares fitting                        # For now, use inverse of sigma_y^2 as weights if available
                        if self.sigma_y is not None and np.all(self.sigma_y > 0):  # type: ignore[misc]
                            weights = 1.0 / (self.sigma_y ** 2)
                        else:
                            weights = np.ones_like(self.y)  # Equal weights
                        resultado, chi2_total, r2 = self.model_manager.perform_weighted_least_squares_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            weights=weights,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            max_iter=max_iter
                        )
                    elif fitting_method == "bootstrap":
                        # Use Bootstrap fitting
                        resultado, chi2_total, r2 = self.model_manager.perform_bootstrap_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            max_iter=max_iter,
                            n_bootstrap=1000  # Could be made configurable
                        )
                    elif fitting_method == "ridge":
                        # Use Ridge regression
                        resultado, chi2_total, r2 = self.model_manager.perform_ridge_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            alpha=1.0,  # Could be made configurable
                            max_iter=max_iter
                        )
                    elif fitting_method == "lasso":
                        # Use Lasso regression
                        resultado, chi2_total, r2 = self.model_manager.perform_lasso_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            alpha=1.0,  # Could be made configurable
                            max_iter=max_iter
                        )
                    elif fitting_method == "bayesian":
                        # Use Bayesian regression
                        resultado, chi2_total, r2 = self.model_manager.perform_bayesian_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            max_iter=max_iter,
                            n_samples=1000  # Could be made configurable
                        )
                    else:
                        # Use ODR fitting (default)
                        # ODR can work with only Y uncertainties, only X uncertainties, or both
                        # The model_manager will handle the uncertainty configuration appropriately
                        resultado, chi2_total, r2 = self.model_manager.perform_odr_fit( # type: ignore[reportUnknownVariableType]
                            x=self.x, y=self.y,
                            sigma_x=self.sigma_x, sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            derivs=derivadas,
                            initial_params=chute,
                            max_iter=max_iter
                        )# Store results
                    self.last_result = resultado
                    self.last_chi2 = float(chi2_total) # chi2_total should be float from perform_odr_fit
                    self.last_r2 = float(r2)         # r2 should be float from perform_odr_fit

                    # Add to history
                    self.history_manager.add_fit_result( # type: ignore[reportUnknownMemberType]
                        resultado, chi2_total, r2, self.equacao, self.parametros
                    )

                    # Update UI - use a simpler approach to avoid callback issues
                    def update_ui_after_fit():
                        try:
                            self.mostrar_resultados(resultado)
                        except Exception as e:
                            logging.error(f"Error updating results display: {e}")                    # Update plot with fitted results - improved approach
                    def update_plot_after_fit():
                        try:
                            if not self.plot_manager:
                                logging.error("Plot manager not available")
                                return
                                
                            # Verify required data is available
                            if not hasattr(self, 'x') or not hasattr(self, 'y'):
                                logging.error("Data arrays (x, y) not available for plotting")
                                return
                                
                            if len(self.x) == 0 or len(self.y) == 0:
                                logging.error("Data arrays (x, y) are empty")
                                return

                            # Clear the plot first to ensure fresh plotting
                            if hasattr(self.plot_manager, 'ax') and self.plot_manager.ax:
                                self.plot_manager.ax.clear()
                            if hasattr(self.plot_manager, 'ax_res') and self.plot_manager.ax_res:
                                self.plot_manager.ax_res.clear()

                            # Try to use plot_fit_results method
                            if hasattr(self.plot_manager, 'plot_fit_results'):
                                logging.info("Attempting to update plot with fit results")
                                
                                # Get current scales and labels
                                x_scale = 'log' if self.x_scale and self.x_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
                                y_scale = 'log' if self.y_scale and self.y_scale.get() == TRANSLATIONS[self.language]['log'] else 'linear'
                                x_label = self.x_label_var.get() if self.x_label_var else "X"
                                y_label = self.y_label_var.get() if self.y_label_var else "Y"
                                title = self.title_entry.get() if self.title_entry else ""
                                
                                self.plot_manager.plot_fit_results(
                                    x=self.x, y=self.y,
                                    sigma_x=self.sigma_x, sigma_y=self.sigma_y,
                                    model_func=modelo_not_none,
                                    result=resultado,
                                    chi2=chi2_total, r2=r2,
                                    equation=self.equacao,
                                    parameters=self.parametros,
                                    x_label=x_label,
                                    y_label=y_label,
                                    title=title,
                                    x_scale=x_scale,
                                    y_scale=y_scale
                                )
                                logging.info("Plot update completed successfully")
                                
                                # Force multiple canvas refreshes to ensure plot is displayed
                                try:
                                    # Schedule multiple redraws to ensure the plot appears
                                    self.plot_manager.canvas.draw_idle()  # Idle draw first
                                    self.parent.update_idletasks()  # Process pending events
                                    self.plot_manager.canvas.draw()  # Force immediate draw
                                    self.plot_manager.canvas.flush_events()  # Flush any pending events
                                    logging.info("Canvas draw and flush completed")
                                    
                                    # Schedule an additional redraw after a short delay
                                    def final_refresh():
                                        try:
                                            self.plot_manager.canvas.draw()
                                            logging.info("Final canvas refresh completed")
                                        except Exception as final_error:
                                            logging.warning(f"Final canvas refresh failed: {final_error}")
                                    
                                    self.parent.after(50, final_refresh)
                                    
                                except Exception as refresh_error:
                                    logging.warning(f"Could not force canvas refresh: {refresh_error}")
                            else:
                                # Fallback: just redraw the canvas
                                logging.warning("plot_fit_results not available, refreshing canvas")
                                if hasattr(self.plot_manager, 'canvas') and self.plot_manager.canvas:
                                    self.plot_manager.canvas.draw()
                                    
                        except Exception as e:
                            logging.error(f"Error updating plot: {e}")
                            import traceback
                            logging.error(f"Plot update traceback: {traceback.format_exc()}")                            # Fallback: try to just refresh the canvas
                            try:
                                if hasattr(self, 'canvas') and self.canvas:
                                    logging.info("Attempting canvas fallback refresh")
                                    self.canvas.draw()
                                elif hasattr(self, 'plot_manager') and hasattr(self.plot_manager, 'canvas') and self.plot_manager.canvas:
                                    logging.info("Attempting plot_manager canvas fallback refresh")
                                    self.plot_manager.canvas.draw()
                                elif hasattr(self, 'plot_manager') and hasattr(self.plot_manager, 'force_refresh'):
                                    logging.info("Attempting plot_manager force refresh")
                                    self.plot_manager.force_refresh()
                                else:
                                    logging.error("No canvas available for fallback refresh")
                            except Exception as canvas_error:
                                logging.error(f"Canvas refresh also failed: {canvas_error}")

                    # Schedule UI updates with improved timing
                    def stop_progress():
                        nonlocal progress_active
                        progress_active = False
                        
                    self.parent.after(5, stop_progress)  # Stop progress first
                    self.parent.after(10, update_ui_after_fit)  # Update results display
                    self.parent.after(200, update_plot_after_fit)  # Longer delay for plot update to ensure data is ready
                    
                    if self.status_label:
                        status_label = self.status_label  # Local reference to avoid closure issues
                        def update_status():
                            try:
                                status_label.config(text=TRANSLATIONS[self.language]['fit_complete'])
                            except Exception as e:
                                logging.error(f"Error updating status: {e}")
                        self.parent.after(100, update_status)

                except (ValueError, TypeError, AttributeError, RuntimeError, ZeroDivisionError) as e:
                    self.parent.after(0, lambda: messagebox.showerror(  # type: ignore[misc]
                        TRANSLATIONS[self.language]['error'],
                        f"{TRANSLATIONS[self.language]['fit_error']}: {str(e)}"
                    ))
                    if self.status_label:
                        status_label = self.status_label  # Local reference to avoid closure issues
                        self.parent.after(0, lambda: status_label.config(
                            text=TRANSLATIONS[self.language]['fit_error'])
                            if status_label else None)            # Progress update function with improved error handling
            progress_active = True
            def update_progress():
                nonlocal progress_active
                if not progress_active:
                    return
                    
                try:
                    if hasattr(self, 'odr') and self.odr is not None and hasattr(self.odr, 'iwork') and self.odr.iwork is not None:
                        try:
                            current_iter = self.odr.iwork[0]
                            if self.progress_var:
                                self.progress_var.set(min(100, current_iter * 10))
                            if self.status_label:
                                status_label = self.status_label  # Local reference for thread safety
                                status_label.config(text=f"Iteração: {current_iter}")
                            if current_iter < max_iter and progress_active:
                                self.parent.after(100, update_progress)
                            else:
                                progress_active = False
                        except (AttributeError, IndexError, TypeError):
                            if progress_active:
                                self.parent.after(100, update_progress)
                    else:
                        # No ODR object, stop progress updates
                        progress_active = False
                except Exception as e:
                    logging.debug(f"Progress update error: {e}")
                    progress_active = False

            # Start progress updates
            self.parent.after(100, update_progress)            # Start fitting in separate thread
            threading.Thread(target=run_fitting, daemon=True).start()

        except (FileNotFoundError, PermissionError, ValueError, TypeError, AttributeError) as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], f"{TRANSLATIONS[self.language]['fit_error']}: {str(e)}")  # type: ignore[misc]
            if self.results_text:
                self.results_text.insert(tk.END, f"{TRANSLATIONS[self.language]['verify_and_retry']}\\n")

    def load_data_and_update_ui(self, file_path: str) -> None:
        """Load data and update UI elements including fitting method visibility
        
        Args:
            file_path: Path to the data file
        """
        try:
            # Load the data using the data handler
            from app_files.gui.ajuste_curva.data_handler import read_file
            data_tuple = read_file(file_path, self.language)
            self.x, self.sigma_x, self.y, self.sigma_y, df = data_tuple
            
            # Update fitting method visibility
            self.update_fitting_method_visibility()            # Update data preview
            if self.data_text:
                self.data_text.delete(1.0, tk.END)
                self.data_text.insert(tk.END, df.to_string(index=False))  # type: ignore[reportUnknownMemberType]
                
        except Exception as e:
            messagebox.showerror(TRANSLATIONS[self.language]['error'], f"Error loading data: {str(e)}")  # type: ignore[misc]

    def on_fitting_method_changed(self, event: tk.Event) -> None:  # type: ignore[reportGeneralTypeIssues]
        """Handle fitting method selection change"""
        if self.ui_builder and hasattr(self.ui_builder, 'fitting_method_var'):
            selected_method = self.ui_builder.fitting_method_var.get()
              # Update UI based on selected method
            if hasattr(self, 'sigma_x') and hasattr(self, 'sigma_y'):
                has_inc_x = not np.allclose(self.sigma_x, 0)
                has_inc_y = not np.allclose(self.sigma_y, 0)
                if not has_inc_y:
                    # 2-column data - only Least Squares is appropriate
                    if "odr" in selected_method.lower():
                        messagebox.showwarning(  # type: ignore[misc]
                            TRANSLATIONS[self.language]['warning'],
                            TRANSLATIONS[self.language]['data_no_uncertainties_warning']
                        )
                        self.ui_builder.fitting_method_var.set(TRANSLATIONS[self.language]['least_squares_method'])
                elif has_inc_x and "least_squares" in selected_method.lower():
                    # 4-column data with Least Squares - warn that inc_x will be ignored
                    messagebox.showwarning(  # type: ignore[misc]
                        TRANSLATIONS[self.language]['warning'],                        TRANSLATIONS[self.language]['least_squares_ignores_inc_x']
                    )
    
    def get_selected_fitting_method(self) -> str:
        """Get the currently selected fitting method"""
        if self.ui_builder and hasattr(self.ui_builder, 'fitting_method_var'):
            method_text = self.ui_builder.fitting_method_var.get()
            if TRANSLATIONS[self.language]['odr_method'] in method_text:
                return "odr"
            elif TRANSLATIONS[self.language]['least_squares_method'] in method_text:
                return "least_squares"
            elif TRANSLATIONS[self.language]['robust_method'] in method_text:
                return "robust"
            elif TRANSLATIONS[self.language]['weighted_method'] in method_text:
                return "weighted"
            elif TRANSLATIONS[self.language]['bootstrap_method'] in method_text:
                return "bootstrap"
            elif TRANSLATIONS[self.language]['ridge_method'] in method_text:
                return "ridge"
            elif TRANSLATIONS[self.language]['lasso_method'] in method_text:
                return "lasso"
            elif TRANSLATIONS[self.language]['bayesian_method'] in method_text:
                return "bayesian"
        return "odr"  # Default fallback
    
    def update_fitting_method_visibility(self) -> None:
        """Update visibility/availability of fitting method dropdown based on data"""
        if self.ui_builder and hasattr(self.ui_builder, 'fitting_method_selector') and self.ui_builder.fitting_method_selector:
            if hasattr(self, 'sigma_x') and hasattr(self, 'sigma_y'):
                has_inc_x = not np.allclose(self.sigma_x, 0)
                has_inc_y = not np.allclose(self.sigma_y, 0)
                
                if not has_inc_y:
                    # 2-column data (x, y) - no uncertainties, only Least Squares makes sense
                    self.ui_builder.fitting_method_selector.config(state="disabled")
                    self.ui_builder.fitting_method_var.set(TRANSLATIONS[self.language]['least_squares_method'])
                elif has_inc_x:
                    # 4-column data (x, inc_x, y, inc_y) - both methods available, default to ODR
                    self.ui_builder.fitting_method_selector.config(state="readonly")
                    self.ui_builder.fitting_method_var.set(TRANSLATIONS[self.language]['odr_method'])
                else:
                    # 3-column data (x, y, inc_y) - both methods available, default to Least Squares
                    self.ui_builder.fitting_method_selector.config(state="readonly")
                    current = self.ui_builder.fitting_method_var.get()
                    if not current:
                        self.ui_builder.fitting_method_var.set(TRANSLATIONS[self.language]['least_squares_method'])
            else:
                # No data loaded yet, disable the selector
                self.ui_builder.fitting_method_selector.config(state="disabled")

    def mostrar_resultados(self, resultado: Any) -> None:
        """Display fitting results in the results text area
        
        Args:
            resultado: The fitting result object (from ODR or Least Squares)
        """
        if not self.results_text:
            return
            
        try:
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Display results header
            results_header = TRANSLATIONS[self.language].get('fit_results_header', 'Resultados do Ajuste')
            self.results_text.insert(tk.END, f"{results_header}\n{'='*50}\n\n")
            
            # Display equation
            if hasattr(self, 'equacao') and self.equacao:
                equation_label = TRANSLATIONS[self.language].get('equation_label', 'Equação')
                self.results_text.insert(tk.END, f"{equation_label}: {self.equacao}\n\n")
            
            # Display parameter values and uncertainties
            if hasattr(resultado, 'beta') and hasattr(resultado, 'sd_beta'):
                params_header = TRANSLATIONS[self.language].get('parameters_header', 'Parâmetros')
                self.results_text.insert(tk.END, f"{params_header}:\n")
                
                beta_values = resultado.beta  # type: ignore[attr-defined]
                sd_beta_values = getattr(resultado, 'sd_beta', None)
                
                if hasattr(self, 'parametros') and self.parametros:
                    for i, param in enumerate(self.parametros):
                        if i < len(beta_values):
                            param_value = beta_values[i]
                            if sd_beta_values is not None and i < len(sd_beta_values):
                                param_error = sd_beta_values[i]
                                self.results_text.insert(tk.END, f"  {param} = {param_value:.6f} ± {param_error:.6f}\n")
                            else:
                                self.results_text.insert(tk.END, f"  {param} = {param_value:.6f}\n")
                else:
                    # Fallback if parameters list is not available
                    for i, value in enumerate(beta_values):
                        if sd_beta_values is not None and i < len(sd_beta_values):
                            error = sd_beta_values[i]
                            self.results_text.insert(tk.END, f"  p{i} = {value:.6f} ± {error:.6f}\n")
                        else:
                            self.results_text.insert(tk.END, f"  p{i} = {value:.6f}\n")
                
                self.results_text.insert(tk.END, "\n")
              # Display goodness of fit statistics
            statistics_header = TRANSLATIONS[self.language].get('statistics_header', 'Estatísticas')
            self.results_text.insert(tk.END, f"{statistics_header}:\n")
            
            if hasattr(self, 'last_chi2'):
                chi2_label = TRANSLATIONS[self.language].get('chi_squared', 'Chi Quadrado')
                self.results_text.insert(tk.END, f"  {chi2_label}: {self.last_chi2:.4f}\n")
                
                # Reduced chi-squared if we have degrees of freedom info
                if hasattr(self, 'x') and hasattr(self, 'parametros') and self.parametros:
                    dof = len(self.x) - len(self.parametros)
                    if dof > 0:
                        reduced_chi2 = self.last_chi2 / dof
                        reduced_chi2_label = TRANSLATIONS[self.language].get('reduced_chi_squared', 'Chi² reduzido')
                        self.results_text.insert(tk.END, f"  {reduced_chi2_label}: {reduced_chi2:.4f}\n")
            
            if hasattr(self, 'last_r2'):
                r2_label = TRANSLATIONS[self.language].get('r_squared', 'R Quadrado')
                self.results_text.insert(tk.END, f"  {r2_label}: {self.last_r2:.4f}\n")
            
            # Display fitting method used
            fitting_method = self.get_selected_fitting_method()
            method_label = TRANSLATIONS[self.language].get('fitting_method_used', 'Método utilizado')
            method_name = TRANSLATIONS[self.language].get('odr_method' if fitting_method == 'odr' else 'least_squares_method', fitting_method)
            self.results_text.insert(tk.END, f"  {method_label}: {method_name}\n")
            
        except Exception as e:
            # If there's an error displaying results, show a basic error message
            error_msg = TRANSLATIONS[self.language].get('display_error', 'Erro ao exibir resultados')
            self.results_text.insert(tk.END, f"{error_msg}: {str(e)}\n")

    def on_tab_activated(self):
        """Handle tab activation event"""
        """Called when this tab becomes active"""
        # Redraw plots if needed
        if hasattr(self, 'plot_manager') and self.plot_manager:
            if hasattr(self.plot_manager, 'canvas'):
                self.plot_manager.canvas.draw()

    def show_advanced_config(self):
        """Show the advanced configuration dialog"""
        self.advanced_config_dialog.show_dialog()

    def update_custom_functions(self, custom_functions: List[CustomFunction]) -> None:
        """Update the list of custom functions from the manager."""
        self.custom_functions = custom_functions

        # Plot the custom functions on the graph
        if self.plot_manager:
            self.plot_manager.plot_custom_functions(custom_functions)

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

    def clear_all_data(self) -> None:
        """Clear all data and reset the interface"""
        # Clear data arrays
        self.x = np.array([])
        self.y = np.array([])
        self.sigma_x = np.array([])
        self.sigma_y = np.array([])
        
        # Clear UI elements
        if self.data_text:
            self.data_text.delete(1.0, tk.END)
        if self.results_text:
            self.results_text.delete(1.0, tk.END)
        if self.equation_entry:
            self.equation_entry.delete(0, tk.END)
        if self.title_entry:
            self.title_entry.delete(0, tk.END)
        if self.file_entry:
            self.file_entry.delete(0, tk.END)
            
        # Reset variables
        if self.x_label_var:
            self.x_label_var.set("X")
        if self.y_label_var:
            self.y_label_var.set("Y")
              # Clear plot
        if hasattr(self, 'plot_manager') and self.plot_manager:
            self.plot_manager.initialize_empty_plot()
              # Reset fit results
        self.last_result = None
        self.modelo = None
        self.odr = None
        
        # Status indicators and fit statistics are no longer in quick actions panel
        # They were removed when the quick actions panel was eliminated

    def update_theme(self) -> None:
        """Update theme colors for all UI components"""
        # Update UI builder components (ScrolledText widgets)
        if hasattr(self, 'ui_builder') and self.ui_builder:
            self.ui_builder.update_theme()
        
        # Update custom function manager tree view colors
        if hasattr(self, 'custom_function_manager') and self.custom_function_manager:
            from app_files.utils.theme_manager import theme_manager
            if hasattr(self.custom_function_manager, 'functions_tree') and self.custom_function_manager.functions_tree:
                try:
                    self.custom_function_manager.functions_tree.tag_configure(
                        "enabled", 
                        foreground=theme_manager.get_adaptive_color('foreground')
                    )
                    self.custom_function_manager.functions_tree.tag_configure(
                        "disabled", 
                        foreground=theme_manager.get_adaptive_color('text_muted')
                    )
                except tk.TclError:
                    pass
