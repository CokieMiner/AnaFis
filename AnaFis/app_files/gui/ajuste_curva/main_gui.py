"""Main GUI class for curve fitting"""

import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from typing import (
    List,
    Optional,
    Callable,
    Union,
    Any,
    cast,
    Tuple,
    Sequence,
)  # Added Sequence
import numpy as np
import numpy.typing as npt
import pandas as pd
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import logging


from app_files.utils.translations.api import get_string
from app_files.utils.theme_manager import theme_manager

from app_files.gui.ajuste_curva.data_handler import read_file

from app_files.gui.ajuste_curva.model_manager import ModelManager
from app_files.gui.ajuste_curva.plot_manager import PlotManager, BetaArray
from app_files.gui.ajuste_curva.adjustment_points_manager import AdjustmentPointsManager
from app_files.gui.ajuste_curva.custom_function_manager import (
    CustomFunctionManager,
    CustomFunction,
)
from app_files.gui.ajuste_curva.advanced_config_dialog import AdvancedConfigDialog
from app_files.gui.ajuste_curva.history_manager import HistoryManager
from app_files.gui.ajuste_curva.ui_builder import UIBuilder
from app_files.gui.ajuste_curva.graph_export_manager import GraphExportManager
from app_files.utils.user_preferences import UserPreferencesManager


# Type aliases for clarity
FloatArray = npt.NDArray[np.float64]
# Adjusted ModelFunction to match ModelCallable from model_manager.py
ModelFunction = Callable[[Sequence[float], FloatArray], FloatArray]
DerivFunction = Callable[
    [Sequence[float], FloatArray], FloatArray
]  # Adjusted to match ModelCallable style
# Corrected CreateModelReturnType: List[DerivFunction] is not Optional
CreateModelReturnType = Tuple[Optional[ModelFunction], List[DerivFunction]]


class AjusteCurvaFrame(tk.Frame):  # Changed to inherit from tk.Frame
    """GUI class for curve fitting"""

    def __init__(
        self, parent: Union[tk.Tk, tk.Toplevel, tk.Widget], language: str = "pt"
    ) -> None:
        """Initialize the GUI

        Args:
            parent: Parent widget (window or frame)
            language: Interface language (default: 'pt')
        """

        super().__init__(parent)  # Call the parent constructor
        self.parent = parent  # Storing the Tk parent widget
        self.language: str = language

        # Only set title if parent is a window
        if isinstance(parent, (tk.Tk, tk.Toplevel)):
            parent.title(
                get_string("curve_fitting", "curve_fitting_title", self.language)
            )

        # Initialize instance variables for data (these don't depend on managers or UI)
        self.x: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.y: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.sigma_x: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.sigma_y: np.ndarray[Any, np.dtype[np.float64]] = np.array([])
        self.cabecalho: List[str] = []
        self.modelo: Optional[ModelFunction] = None

        # Data file tracking for format override
        self.current_file_path: Optional[str] = None
        self.current_raw_data: Optional[npt.NDArray[np.float64]] = None
        self.current_num_columns: int = 0
        self.current_format: str = ""  # Track detected/current format
        self.using_custom_assignment: bool = (
            False  # Flag to track if custom column assignment is active
        )

        # Initialize managers that UIBuilder's setup_ui() might depend on
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
        self._setup_plot_area()  # Initialize other managers that depend on the canvas or fully constructed UI
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
            self.language,
        )

        # Model and fitting variables
        self.equacao = ""
        self.parametros: List[sp.Symbol] = []
        self.odr = None
        # Last results
        self.last_result: Any = None
        self.last_chi2: float = 0.0
        self.last_r2: float = 0.0  # Additional attributes to avoid pylint warnings
        self.custom_functions: List[CustomFunction] = []
        self.adjustment_points_selection_mode: str = get_string(
            "curve_fitting", "all_points_value", self.language
        )
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
        if hasattr(self, "fig") and self.fig:
            plt.close(self.fig)

        # Configure matplotlib to suppress icon warnings
        import matplotlib as mpl

        mpl.rcParams["figure.max_open_warning"] = 0  # Suppress too many figures warning

        # Ensure we're in the main thread for GUI operations
        import threading

        if threading.current_thread() != threading.main_thread():
            logging.warning("Plot creation called from non-main thread")
            # Schedule plot creation in main thread
            self.after_idle(self._setup_plot_area)
            return
        # Use Any to avoid complex type issues with matplotlib
        # Create subplots with height ratios: main plot gets 4x more space than residuals
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [4, 1]})
        self.fig = fig

        # Set icon handling to avoid conflicts
        fig.canvas.manager.set_window_title("AnaFis - Curve Fitting")
        # Matplotlib returns either a single Axes or an array of Axes depending on inputs
        # For 2x1 subplots with default squeeze=True, it returns an array
        # Use Any to bypass type checking complications
        self.ax: Any = axes[0] if hasattr(axes, "__len__") else axes
        self.ax_res: Any = axes[1] if hasattr(axes, "__len__") else None

        # Create new canvas
        if self.ui_builder.plot_area_frame is None:
            raise RuntimeError("UIBuilder did not create the plot_area_frame.")

        self.canvas = FigureCanvasTkAgg(
            self.fig, master=self.ui_builder.plot_area_frame
        )
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(highlightthickness=0)
        canvas_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Initialize plot manager with new canvas
        self.plot_manager = PlotManager(
            self.fig, self.ax, self.ax_res, self.canvas, self.language
        )

    # Forward UI element access to the UI builder with more concise implementation
    def _get_ui_attr(self, attr_name: str) -> Any:
        """Helper method to safely get UI attributes"""
        return (
            getattr(self.ui_builder, attr_name)
            if hasattr(self, "ui_builder")
            and self.ui_builder
            and hasattr(self.ui_builder, attr_name)
            else None
        )

    # UI property getters - All use _get_ui_attr for consistent access pattern
    @property
    def data_text(self) -> Optional[tk.Text]:
        return self._get_ui_attr("data_text")

    @property
    def results_text(self) -> Optional[tk.Text]:
        return self._get_ui_attr("results_text")

    @property
    def title_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr("title_entry")

    @property
    def x_label_var(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr("x_label_var")

    @property
    def y_label_var(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr("y_label_var")

    @property
    def x_scale(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr("x_scale")

    @property
    def y_scale(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr("y_scale")

    @property
    def file_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr("file_entry")

    @property
    def equation_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr("equation_entry")

    @property
    def model_selector(self) -> Optional[tk.StringVar]:
        return self._get_ui_attr("model_selector")

    @property
    def num_points_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr("num_points_entry")

    @property
    def max_iter_entry(self) -> Optional[tk.Entry]:
        return self._get_ui_attr("max_iter_entry")

    @property
    def progress_var(self) -> Optional[tk.IntVar]:
        return self._get_ui_attr("progress_var")

    @property
    def status_label(self) -> Optional[tk.Label]:
        return self._get_ui_attr("status_label")

    @property
    def save_graph_option(self) -> Optional[tk.StringVar]:  # Changed from tk.BooleanVar
        return self._get_ui_attr("save_graph_option")

    def update_data_preview(self, data: pd.DataFrame) -> None:
        """Update data preview text widget - showing all data"""
        if self.data_text:
            self.data_text.delete(1.0, tk.END)
            preview_str = data.to_string(index=False, float_format="%.4f")
            self.data_text.insert(1.0, preview_str)  # Update plot with data immediately
            self.plot_data_only()

    def plot_data_only(self):
        """Plot only the data points without any curve fitting"""
        try:
            logging.info("plot_data_only called")

            if len(self.x) == 0 or len(self.y) == 0:
                logging.warning("No data available to plot (empty arrays)")
                return

            # Get scales and labels with fallbacks
            x_scale = (
                "log"
                if self.x_scale
                and self.x_scale.get()
                == get_string("curve_fitting", "log", self.language)
                else "linear"
            )
            y_scale = (
                "log"
                if self.y_scale
                and self.y_scale.get()
                == get_string("curve_fitting", "log", self.language)
                else "linear"
            )
            x_label = self.x_label_var.get() if self.x_label_var else "X"
            y_label = self.y_label_var.get() if self.y_label_var else "Y"
            title = (
                self.ui_builder.title_var.get()
                if hasattr(self.ui_builder, "title_var")
                else ""
            )

            logging.info(
                f"Plotting data: {len(self.x)} points, x_scale={x_scale}, y_scale={y_scale}"
            )

            self.plot_manager.plot_data_only(
                self.x,
                self.y,
                self.sigma_x,
                self.sigma_y,
                x_label=x_label,
                y_label=y_label,
                title=title,
                x_scale=x_scale,
                y_scale=y_scale,
            )

            # Force canvas redraw
            if hasattr(self.plot_manager, "canvas") and self.plot_manager.canvas:
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
            title=get_string("curve_fitting", "select_data_file", self.language),
            filetypes=[
                (
                    get_string("curve_fitting", "all_compatible", self.language),
                    "*.xlsx *.xls *.txt *.csv *.json",
                ),
                (
                    get_string("curve_fitting", "excel_files", self.language),
                    "*.xlsx *.xls",
                ),
                (
                    get_string("curve_fitting", "text_csv_files", self.language),
                    "*.txt *.csv",
                ),
                (get_string("curve_fitting", "json_files", self.language), "*.json"),
                (get_string("curve_fitting", "all_files", self.language), "*.*"),
            ],
        )
        if filename and self.file_entry:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            # Automatically load data when file is selected
            try:
                data_tuple = read_file(filename, self.language)
                # No cast needed if read_file has proper return type annotation and Pylance infers it
                self.x, self.sigma_x, self.y, self.sigma_y, df = data_tuple

                # Store file path and detect format for override feature
                self.current_file_path = filename
                self._detect_and_store_format(
                    filename, self.x, self.sigma_x, self.y, self.sigma_y
                )

                # Reset custom assignment flag when loading a new file
                self.using_custom_assignment = False

                self.update_data_preview(df)
                with open(filename, "r", encoding="utf-8") as f:
                    try:
                        self.cabecalho = f.readline().strip().split("\t")
                    except (UnicodeDecodeError, AttributeError, ValueError):
                        self.cabecalho = [
                            "x",
                            "sigma_x",
                            "y",
                            "sigma_y",
                        ]  # Plotar dados imediatamente após carregar
                self.parent.after(100, self.plot_data_only)

            except (
                FileNotFoundError,
                PermissionError,
                IOError,
                ValueError,
                TypeError,
            ) as e:  # Log the error for debugging while maintaining user experience
                logging.debug(f"Error loading file: {e}")
                # Error handling is already done in read_file method

    def show_format_override_dialog(self):
        """Show dialog to override automatic column format detection with full flexibility"""
        if self.current_num_columns < 2:
            messagebox.showinfo(
                get_string("curve_fitting", "info", self.language),
                get_string("curve_fitting", "no_data_loaded_reinterpret", self.language),
            )
            return

        # Create dialog with minimal height based on number of columns
        dialog = tk.Toplevel(self)
        dialog.title(get_string("curve_fitting", "column_assignment_title", self.language))

        # Calculate height: base(90) + columns(30 each) + buttons(50)
        dialog_height = 90 + (self.current_num_columns * 30) + 50
        dialog.geometry(f"400x{dialog_height}")
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"400x{dialog_height}+{x}+{y}")

        # Header - compact
        header_text = get_string("curve_fitting", "assign_columns", self.language)
        ttk.Label(dialog, text=header_text, font=("", 10, "bold")).pack(pady=(8, 3))

        # Current format display - compact
        current_text_template = get_string("curve_fitting", "current_format", self.language)
        try:
            current_text = current_text_template.format(self.current_format)
        except Exception:
            current_text = f"{self.current_format}"
        ttk.Label(dialog, text=current_text, foreground="blue", font=("", 8)).pack(
            pady=(0, 8)
        )

        # Dropdown options
        options = [
                get_string("curve_fitting", "option_x", self.language),
                get_string("curve_fitting", "option_y", self.language),
            get_string("curve_fitting", "option_sigx", self.language),
            get_string("curve_fitting", "option_sigy", self.language),
            get_string("curve_fitting", "option_ignore", self.language),
        ]

        # Frame for column assignments
        assign_frame = ttk.Frame(dialog)
        assign_frame.pack(pady=0, padx=15, fill="x")

        # Create dropdowns for each column
        column_vars = []
        # Map displayed option text back to internal keys used in logic
        display_to_key = {
            options[0]: "x",
            options[1]: "y",
            options[2]: "sig_x",
            options[3]: "sig_y",
            options[4]: "ignore",
        }

        for i in range(self.current_num_columns):
            row_frame = ttk.Frame(assign_frame)
            row_frame.pack(fill="x", pady=2)

            col_label = ttk.Label(
                row_frame,
                text=f"Col {i+1}:",
                width=7,
                anchor="w",
                font=("", 9),
            )
            col_label.pack(side="left", padx=(0, 5))

            var = tk.StringVar()
            dropdown = ttk.Combobox(
                row_frame,
                textvariable=var,
                values=options,
                state="readonly",
                width=20,
                font=("", 9),
            )
            dropdown.pack(side="left", padx=0)
            column_vars.append(var)

            # Set default based on current interpretation using displayed option strings
            if i == 0:
                var.set(options[0])
            elif self.current_num_columns == 2:
                var.set(options[1])
            elif self.current_num_columns == 3:
                # Try to detect current format
                if not np.allclose(self.sigma_x, 0) and i == 1:
                    var.set(options[2])
                elif not np.allclose(self.sigma_y, 0) and i == 2:
                    var.set(options[3])
                elif i == 1 and np.allclose(self.sigma_x, 0):
                    var.set(options[1])
                elif i == 2:
                    var.set(options[3] if np.allclose(self.sigma_x, 0) else options[1])
            elif self.current_num_columns >= 4:
                defaults = [options[0], options[2], options[1], options[3]]
                if i < len(defaults):
                    var.set(defaults[i])

        # Validation message
        validation_label = ttk.Label(dialog, text="", foreground="red", font=("", 8))
        validation_label.pack(pady=(3, 0))

        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=8)

        def apply_assignment():
            # Validate: must have x and y
            displayed_assignments = [var.get() for var in column_vars]
            # Convert displayed texts back to internal keys
            assignments = [display_to_key.get(a, a) for a in displayed_assignments]

            if "x" not in assignments:
                validation_label.config(
                    text=get_string("curve_fitting", "must_assign_x", self.language)
                )
                return
            if "y" not in assignments:
                validation_label.config(
                    text=get_string("curve_fitting", "must_assign_y", self.language)
                )
                return
            if assignments.count("x") > 1 or assignments.count("y") > 1:
                validation_label.config(
                    text=get_string("curve_fitting", "each_type_once", self.language)
                )
                return

            # Apply the custom assignment
            self.apply_custom_column_assignment(assignments)
            dialog.destroy()

        ttk.Button(
            btn_frame,
            text=get_string("curve_fitting", "apply", self.language),
            command=apply_assignment,
            width=10,
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text=get_string("curve_fitting", "cancel", self.language),
            command=dialog.destroy,
            width=10,
        ).pack(side="left", padx=5)

    def apply_custom_column_assignment(self, assignments: List[str]):
        """Apply custom column assignments from user selection

        Args:
            assignments: List of assignments for each column (e.g., ['x', 'sig_x', 'y', 'sig_y', 'ignore'])
        """
        if self.current_raw_data is None:
            return

        data = self.current_raw_data

        # Initialize arrays
        x_data = None
        y_data = None
        sigma_x_data = None
        sigma_y_data = None

        # Extract data based on assignments (using internal keys)
        for i, assignment in enumerate(assignments):
            if assignment == "x":
                x_data = data[:, i].astype(np.float64)
            elif assignment == "y":
                y_data = data[:, i].astype(np.float64)
            elif assignment == "sig_x":
                sigma_x_data = data[:, i].astype(np.float64)
            elif assignment == "sig_y":
                sigma_y_data = data[:, i].astype(np.float64)
            # "ignore" columns are simply skipped

        # Set data with defaults for missing uncertainties
        if x_data is not None:
            self.x = x_data
            self.sigma_x = (
                sigma_x_data if sigma_x_data is not None else np.zeros_like(x_data)
            )
        if y_data is not None:
            self.y = y_data
            self.sigma_y = (
                sigma_y_data if sigma_y_data is not None else np.zeros_like(y_data)
            )

        # Mark that custom assignment is active
        self.using_custom_assignment = True

        # Update current format description (using internal keys)
        format_parts = []
        for assignment in assignments:
            if assignment == "ignore":
                continue
            elif assignment == "sig_x":
                format_parts.append("σx")
            elif assignment == "sig_y":
                format_parts.append("σy")
            else:
                format_parts.append(assignment)

        self.current_format = f"{self.current_num_columns} columns: " + ", ".join(
            format_parts
        )

        # Update UI
        if hasattr(self.ui_builder, "format_label"):
            format_text = get_string(
                "curve_fitting", "data_format_detected", self.language
            ).format(self.current_format)
            self.ui_builder.format_label.config(
                text=format_text, foreground="darkgreen"
            )

        # Update data preview
        df = pd.DataFrame(
            {"x": self.x, "sigma_x": self.sigma_x, "y": self.y, "sigma_y": self.sigma_y}
        )
        self.update_data_preview(df)

        # Update fitting method visibility
        self.update_fitting_method_visibility()

        # Replot data
        self.parent.after(100, self.plot_data_only)

        # Show confirmation
        title = get_string("curve_fitting", "format_changed_title", self.language)
        msg_template = get_string(
            "curve_fitting", "format_changed_message", self.language
        )
        try:
            message = msg_template.format(
                ", ".join(format_parts)
            )
        except Exception:
            message = f"Columns reassigned: {', '.join(format_parts)}"
        messagebox.showinfo(title, message)

    def _detect_and_store_format(
        self,
        filename: str,
        x: npt.NDArray[np.float64],
        sigma_x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        sigma_y: npt.NDArray[np.float64],
    ) -> None:
        """Detect data format and store raw data for potential re-interpretation

        Args:
            filename: Path to the loaded file
            x, sigma_x, y, sigma_y: The loaded data arrays
        """
        import os

        # Load raw data for re-interpretation
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        try:
            if ext in [".txt", ".csv"]:
                # Skip comments and read raw numeric data
                self.current_raw_data = np.genfromtxt(filename, comments="#")
            elif ext in [".xlsx", ".xls"]:
                df_raw = pd.read_excel(filename)
                self.current_raw_data = df_raw.to_numpy(dtype=float)
            else:
                # JSON or other format - can't easily re-interpret
                self.current_raw_data = None

            # Detect number of columns
            if self.current_raw_data is not None:
                if len(self.current_raw_data.shape) == 1:
                    self.current_num_columns = 1
                else:
                    self.current_num_columns = self.current_raw_data.shape[1]
            else:
                self.current_num_columns = 0

            # Detect current format based on loaded data patterns
            has_sigma_x = not np.allclose(sigma_x, 0)
            has_sigma_y = not np.allclose(sigma_y, 0)

            if not has_sigma_x and not has_sigma_y:
                self.current_format = get_string(
                    "curve_fitting", "format_2col", self.language
                )
                self.current_num_columns = 2
            elif self.current_num_columns == 3:
                if has_sigma_x:
                    self.current_format = get_string(
                        "curve_fitting", "format_3col_x_sigx_y", self.language
                    )
                else:
                    self.current_format = get_string(
                        "curve_fitting", "format_3col_xy_sigy", self.language
                    )
            elif self.current_num_columns >= 4:
                # For 4 columns, use detection function to determine ordering
                from app_files.gui.ajuste_curva.data_handler import (
                    detect_4column_format,
                )

                format_type = detect_4column_format(filename, None)
                if format_type == "x_y_sigmax_sigmay":
                    self.current_format = get_string(
                        "curve_fitting", "format_4col_alt", self.language
                    )
                else:
                    self.current_format = get_string(
                        "curve_fitting", "format_4col_standard", self.language
                    )
            else:
                self.current_format = "Unknown"

            # Update format label in UI
            if hasattr(self.ui_builder, "format_label"):
                format_text = get_string(
                    "curve_fitting", "data_format_detected", self.language
                ).format(self.current_format)
                self.ui_builder.format_label.config(
                    text=format_text, foreground="darkgreen"
                )

            # Enable re-interpret button for any valid data file
            if hasattr(self.ui_builder, "reinterpret_btn"):
                if self.current_num_columns >= 2:
                    self.ui_builder.reinterpret_btn.config(state="normal")
                else:
                    self.ui_builder.reinterpret_btn.config(state="disabled")

        except Exception as e:
            logging.debug(f"Error detecting format: {e}")
            self.current_raw_data = None
            self.current_num_columns = 0
            self.current_format = "Unknown"

    def update_scales(self):
        """Update plot scales based on user selection and redraw plot"""
        if len(self.x) == 0 or len(self.y) == 0 or not self.x_scale or not self.y_scale:
            return

        # Get scales
        x_scale = (
            "log"
            if self.x_scale.get() == get_string("curve_fitting", "log", self.language)
            else "linear"
        )
        y_scale = (
            "log"
            if self.y_scale.get() == get_string("curve_fitting", "log", self.language)
            else "linear"
        )

        # Get current labels and title
        x_label = self.x_label_var.get() if self.x_label_var else "X"
        y_label = self.y_label_var.get() if self.y_label_var else "Y"
        title = (
            self.ui_builder.title_var.get()
            if hasattr(self.ui_builder, "title_var")
            else ""
        )

        # Check if we have a fitted model - if so, replot with fit results
        if (
            hasattr(self, "last_result")
            and self.last_result is not None
            and hasattr(self, "modelo")
            and self.modelo is not None
        ):
            # Replot with fit results to preserve the fit
            modelo_not_none = cast(ModelFunction, self.modelo)
            self.plot_manager.plot_fit_results(
                x=self.x,
                y=self.y,
                sigma_x=self.sigma_x,
                sigma_y=self.sigma_y,
                model_func=modelo_not_none,
                result=self.last_result,
                chi2=self.last_chi2,
                r2=self.last_r2,
                equation=self.equacao,
                parameters=self.parametros,
                x_label=x_label,
                y_label=y_label,
                title=title,
                x_scale=x_scale,
                y_scale=y_scale,
            )
        else:
            # No fit exists, just plot data
            self.plot_manager.plot_data_only(
                x=self.x,
                y=self.y,
                sigma_x=self.sigma_x,
                sigma_y=self.sigma_y,
                x_label=x_label,
                y_label=y_label,
                title=title,
                x_scale=x_scale,
                y_scale=y_scale,
            )

    def update_graph_labels(self):
        """Update graph title and axis labels without redrawing data/fits"""
        if not hasattr(self, "plot_manager") or not self.plot_manager:
            return

        # Get label values from UI
        title = (
            self.ui_builder.title_var.get()
            if hasattr(self.ui_builder, "title_var")
            else ""
        )
        x_label = (
            self.ui_builder.x_label_var.get()
            if hasattr(self.ui_builder, "x_label_var")
            else "X"
        )
        y_label = (
            self.ui_builder.y_label_var.get()
            if hasattr(self.ui_builder, "y_label_var")
            else "Y"
        )

        # If title is empty and we have a fit, create default title from equation
        if not title and hasattr(self, "last_result") and self.last_result is not None:
            if hasattr(self, "equacao") and hasattr(self, "parametros"):
                eq_title = self.equacao
                beta_values = cast(BetaArray, self.last_result.beta)
                for i, p_sym in enumerate(self.parametros):
                    eq_title = eq_title.replace(
                        str(p_sym), f"{str(p_sym)}={beta_values[i]:.4f}"
                    )
                title = f"{get_string('curve_fitting', 'fit_title_prefix', self.language)}: {eq_title}"

        # Update main plot labels
        if hasattr(self.plot_manager, "ax"):
            self.plot_manager.ax.set_title(title)
            self.plot_manager.ax.set_xlabel(x_label)
            self.plot_manager.ax.set_ylabel(y_label)

        # Update residuals plot x-label
        if hasattr(self.plot_manager, "ax_res"):
            self.plot_manager.ax_res.set_xlabel(x_label)

        # Redraw canvas to show changes (but don't replot data)
        if hasattr(self.plot_manager, "canvas"):
            self.plot_manager.canvas.draw_idle()

    def apply_preset_model(self, _event: Optional[tk.Event] = None) -> None:
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

    def validate_equation(
        self, _event: Optional[Any] = None
    ) -> bool:  # Changed _event type hint
        """Validate equation in real-time

        Args:
            _event: Event parameter required by tkinter binding but not used

        Returns:
            bool: True if equation is valid, False otherwise
        """
        if not self.equation_entry:
            return False

        equation = self.equation_entry.get().replace("^", "**")
        try:
            if "=" in equation:
                equation = equation.split("=")[1].strip()
                # Use the comprehensive supported functions from model_manager
                sp.sympify(equation, locals=self.model_manager.SUPPORTED_SYMPY_OBJECTS)
            # Use theme-appropriate color for valid equation
            valid_color = theme_manager.get_adaptive_color("text_valid")
            self.equation_entry.configure(foreground=valid_color)
            return True
        except (ValueError, TypeError, SyntaxError):
            # Use theme-appropriate color for error
            error_color = theme_manager.get_adaptive_color("text_error")
            self.equation_entry.configure(foreground=error_color)
            return False

    def update_estimates_frame(self):
        """Update the parameter estimates frame based on current equation"""
        if not self.equation_entry:
            return

        equation = self.equation_entry.get()
        if equation:
            self.parameter_estimates_manager.update_estimates_frame(equation)            # Update parametros for compatibility with other parts of the code
            self.parametros = self.parameter_estimates_manager.parameters

    def save_graph(self):
        """Save the current graph to file"""
        print("[DEBUG] save_graph method called on AjusteCurvaFrame")
        self.graph_export_manager.save_graph()

    def perform_fit(self):
        """Perform the curve fitting operation"""
        if not self.num_points_entry:
            messagebox.showerror(
                get_string("curve_fitting", "error", self.language),
                get_string("curve_fitting", "invalid_points", self.language),
            )
            return

        try:
            num_points = int(self.num_points_entry.get())
            if num_points <= 0:
                raise ValueError(
                    get_string("curve_fitting", "positive_points", self.language)
                )
        except ValueError:
            messagebox.showerror(get_string("curve_fitting", "error", self.language), get_string("curve_fitting", "invalid_points", self.language))
            return

        try:
            # Reset progress and status
            if self.progress_var:
                self.progress_var.set(0)
            if self.status_label:
                self.status_label.config(
                    text=get_string("curve_fitting", "starting_fit", self.language)
                )
            self.parent.update()

            # Clear previous results
            if self.results_text:
                self.results_text.delete(1.0, tk.END)  # Update estimates if needed
            if not self.parametros:
                self.update_estimates_frame()

            # Get field values
            if (
                not self.file_entry
                or not self.equation_entry
                or not self.max_iter_entry
            ):
                messagebox.showerror(
                    get_string("curve_fitting", "error", self.language),
                    "UI elements not initialized properly",
                )
                return

            # Type narrowing: assert entries are not None after the check above
            assert self.file_entry is not None
            assert self.equation_entry is not None
            assert self.max_iter_entry is not None

            caminho = self.file_entry.get()
            equacao = self.equation_entry.get().replace("^", "**")
            if "=" in equacao:
                equacao = equacao.split("=")[1].strip()
            max_iter = int(self.max_iter_entry.get())

            # Check if file path is provided
            if not caminho or caminho.strip() == "":
                messagebox.showerror(
                    get_string("curve_fitting", "error", self.language),
                    get_string("curve_fitting", "select_file_first", self.language),
                )
                return

            # Get initial estimates from parameter manager
            chute = self.parameter_estimates_manager.get_initial_estimates()
            # No cast needed if get_initial_estimates has proper return type annotation

            # Load data only if we're not using custom column assignments
            # If custom assignments are active, data is already loaded in self.x, self.y, etc.
            if not self.using_custom_assignment:
                data_tuple = read_file(caminho, self.language)
                # No cast needed if read_file has proper return type annotation
                self.x, self.sigma_x, self.y, self.sigma_y, _ = data_tuple

            # Validate loaded data
            if len(self.x) == 0 or len(self.y) == 0:
                messagebox.showerror(
                    get_string("curve_fitting", "error", self.language),
                    "Data file appears to be empty or invalid",
                )
                return

            if len(self.x) != len(self.y):
                messagebox.showerror(
                    get_string("curve_fitting", "error", self.language),
                    "X and Y data arrays have different lengths",
                )
                return

            with open(caminho, "r", encoding="utf-8") as f:
                self.cabecalho = f.readline().strip().split("\\\\t")

            # Create model
            model_result_tuple = self.model_manager.create_model(equacao, self.parametros)
            # Cast is appropriate here if Pylance cannot infer the precise tuple structure from create_model
            typed_model_result = cast(CreateModelReturnType, model_result_tuple)
            self.modelo, derivadas = typed_model_result

            if self.modelo is None:
                raise RuntimeError(
                    "Model function is not initialized."
                )  # Store equation for later use
            self.equacao = equacao

            def run_fitting():
                try:
                    # Get the selected fitting method
                    fitting_method = self.get_selected_fitting_method()
                    # Use cast to ensure self.modelo is not None when passed to fitting methods
                    modelo_not_none = cast(ModelFunction, self.modelo)

                    if fitting_method == "least_squares":
                        # Use Least Squares fitting
                        resultado, chi2_total, r2 = self.model_manager.perform_least_squares_fit(
                            x=self.x,
                            y=self.y,
                            sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            max_iter=max_iter,
                        )
                    elif fitting_method == "robust":
                        # Use Robust fitting (RANSAC/Huber)
                        resultado, chi2_total, r2 = self.model_manager.perform_robust_fit(
                            x=self.x,
                            y=self.y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            method="ransac",  # Could be made configurable
                            max_iter=max_iter,
                        )
                    elif fitting_method == "bootstrap":
                        # Use Bootstrap fitting
                        resultado, chi2_total, r2 = self.model_manager.perform_bootstrap_fit(
                            x=self.x,
                            y=self.y,
                            sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            max_iter=max_iter,
                            n_bootstrap=1000,  # Could be made configurable
                        )
                    elif fitting_method == "bayesian":
                        # Use Bayesian regression
                        resultado, chi2_total, r2 = self.model_manager.perform_bayesian_fit(
                            x=self.x,
                            y=self.y,
                            sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            initial_params=chute,
                            max_iter=max_iter,
                            n_samples=1000,  # Could be made configurable
                        )
                    else:
                        # Use ODR fitting (default)
                        # ODR can work with only Y uncertainties, only X uncertainties, or both
                        # The model_manager will handle the uncertainty configuration appropriately
                        resultado, chi2_total, r2 = self.model_manager.perform_odr_fit(
                            x=self.x,
                            y=self.y,
                            sigma_x=self.sigma_x,
                            sigma_y=self.sigma_y,
                            model_func=modelo_not_none,
                            derivs=derivadas,
                            initial_params=chute,
                            max_iter=max_iter,
                        )  # Store results
                    self.last_result = resultado
                    self.last_chi2 = float(
                        chi2_total
                    )  # chi2_total should be float from perform_odr_fit
                    self.last_r2 = float(r2)  # r2 should be float from perform_odr_fit

                    # Add to history
                    self.history_manager.add_fit_result(
                        resultado, chi2_total, r2, self.equacao, self.parametros
                    )

                    # Update UI - use a simpler approach to avoid callback issues
                    def update_ui_after_fit():
                        try:
                            self.mostrar_resultados(resultado)
                        except Exception as e:
                            logging.error(
                                f"Error updating results display: {e}"
                            )  # Update plot with fitted results - improved approach

                    def update_plot_after_fit():
                        try:
                            if not self.plot_manager:
                                logging.error("Plot manager not available")
                                return

                            # Verify required data is available
                            if not hasattr(self, "x") or not hasattr(self, "y"):
                                logging.error(
                                    "Data arrays (x, y) not available for plotting"
                                )
                                return

                            if len(self.x) == 0 or len(self.y) == 0:
                                logging.error("Data arrays (x, y) are empty")
                                return

                            # Clear the plot first to ensure fresh plotting
                            if (
                                hasattr(self.plot_manager, "ax")
                                and self.plot_manager.ax
                            ):
                                self.plot_manager.ax.clear()
                            if (
                                hasattr(self.plot_manager, "ax_res")
                                and self.plot_manager.ax_res
                            ):
                                self.plot_manager.ax_res.clear()

                            # Try to use plot_fit_results method
                            if hasattr(self.plot_manager, "plot_fit_results"):
                                logging.info(
                                    "Attempting to update plot with fit results"
                                )

                                # Get current scales and labels
                                x_scale = (
                                    "log"
                                    if self.x_scale
                                    and self.x_scale.get()
                                    == get_string("curve_fitting", "log", self.language)
                                    else "linear"
                                )
                                y_scale = (
                                    "log"
                                    if self.y_scale
                                    and self.y_scale.get()
                                    == get_string("curve_fitting", "log", self.language)
                                    else "linear"
                                )
                                x_label = (
                                    self.x_label_var.get() if self.x_label_var else "X"
                                )
                                y_label = (
                                    self.y_label_var.get() if self.y_label_var else "Y"
                                )
                                title = (
                                    self.ui_builder.title_var.get()
                                    if hasattr(self.ui_builder, "title_var")
                                    else ""
                                )

                                self.plot_manager.plot_fit_results(
                                    x=self.x,
                                    y=self.y,
                                    sigma_x=self.sigma_x,
                                    sigma_y=self.sigma_y,
                                    model_func=modelo_not_none,
                                    result=resultado,
                                    chi2=chi2_total,
                                    r2=r2,
                                    equation=self.equacao,
                                    parameters=self.parametros,
                                    x_label=x_label,
                                    y_label=y_label,
                                    title=title,
                                    x_scale=x_scale,
                                    y_scale=y_scale,
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
                                            logging.info(
                                                "Final canvas refresh completed"
                                            )
                                        except Exception as final_error:
                                            logging.warning(
                                                f"Final canvas refresh failed: {final_error}"
                                            )

                                    self.parent.after(50, final_refresh)

                                except Exception as refresh_error:
                                    logging.warning(
                                        f"Could not force canvas refresh: {refresh_error}"
                                    )
                            else:
                                # Fallback: just redraw the canvas
                                logging.warning(
                                    "plot_fit_results not available, refreshing canvas"
                                )
                                if (
                                    hasattr(self.plot_manager, "canvas")
                                    and self.plot_manager.canvas
                                ):
                                    self.plot_manager.canvas.draw()

                        except Exception as e:
                            logging.error(f"Error updating plot: {e}")
                            import traceback

                            logging.error(
                                f"Plot update traceback: {traceback.format_exc()}"
                            )  # Fallback: try to just refresh the canvas
                            try:
                                if hasattr(self, "canvas") and self.canvas:
                                    logging.info("Attempting canvas fallback refresh")
                                    self.canvas.draw()
                                elif (
                                    hasattr(self, "plot_manager")
                                    and hasattr(self.plot_manager, "canvas")
                                    and self.plot_manager.canvas
                                ):
                                    logging.info(
                                        "Attempting plot_manager canvas fallback refresh"
                                    )
                                    self.plot_manager.canvas.draw()
                                elif hasattr(self, "plot_manager") and hasattr(
                                    self.plot_manager, "force_refresh"
                                ):
                                    logging.info(
                                        "Attempting plot_manager force refresh"
                                    )
                                    self.plot_manager.force_refresh()
                                else:
                                    logging.error(
                                        "No canvas available for fallback refresh"
                                    )
                            except Exception as canvas_error:
                                logging.error(
                                    f"Canvas refresh also failed: {canvas_error}"
                                )

                    # Schedule UI updates with improved timing
                    def stop_progress():
                        nonlocal progress_active
                        progress_active = False

                    self.parent.after(5, stop_progress)  # Stop progress first
                    self.parent.after(10, update_ui_after_fit)  # Update results display
                    self.parent.after(
                        200, update_plot_after_fit
                    )  # Longer delay for plot update to ensure data is ready

                    if self.status_label:
                        status_label = (
                            self.status_label
                        )  # Local reference to avoid closure issues

                        def update_status():
                            try:
                                status_label.config(
                                    text=get_string(
                                        "curve_fitting", "fit_complete", self.language
                                    )
                                )
                            except Exception as e:
                                logging.error(f"Error updating status: {e}")

                        self.parent.after(100, update_status)

                except (
                    ValueError,
                    TypeError,
                    AttributeError,
                    RuntimeError,
                    ZeroDivisionError,
                ) as e:
                    self.parent.after(
                        0,
                        lambda: messagebox.showerror(
                            get_string("curve_fitting", "error", self.language),
                            f"{get_string('curve_fitting', 'fit_error', self.language)}: {str(e)}",
                        ),
                    )
                    if self.status_label:
                        status_label = (
                            self.status_label
                        )  # Local reference to avoid closure issues
                        self.parent.after(
                            0,
                            lambda: (
                                status_label.config(
                                    text=get_string(
                                        "curve_fitting", "fit_error", self.language
                                    )
                                )
                                if status_label
                                else None
                            ),
                        )  # Progress update function with improved error handling

            progress_active = True

            def update_progress():
                nonlocal progress_active
                if not progress_active:
                    return

                try:
                    if (
                        hasattr(self, "odr")
                        and self.odr is not None
                        and hasattr(self.odr, "iwork")
                        and self.odr.iwork is not None
                    ):
                        try:
                            current_iter = self.odr.iwork[0]
                            if self.progress_var:
                                self.progress_var.set(min(100, current_iter * 10))
                            if self.status_label:
                                status_label = (
                                    self.status_label
                                )  # Local reference for thread safety
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
            self.parent.after(100, update_progress)  # Start fitting in separate thread
            threading.Thread(target=run_fitting, daemon=True).start()

        except (
            FileNotFoundError,
            PermissionError,
            ValueError,
            TypeError,
            AttributeError,
        ) as e:
            messagebox.showerror(get_string("curve_fitting", "error", self.language), f"{get_string('curve_fitting', 'fit_error', self.language)}: {str(e)}")
            if self.results_text:
                self.results_text.insert(
                    tk.END,
                    f"{get_string('curve_fitting', 'verify_and_retry', self.language)}\\n",
                )

    def on_fitting_method_changed(self, event: tk.Event) -> None: 
        """Handle fitting method selection change"""
        if self.ui_builder and hasattr(self.ui_builder, "fitting_method_var"):
            selected_method = self.ui_builder.fitting_method_var.get()
            # Update UI based on selected method
            if hasattr(self, "sigma_x") and hasattr(self, "sigma_y"):
                has_inc_x = not np.allclose(self.sigma_x, 0)
                has_inc_y = not np.allclose(self.sigma_y, 0)
                if not has_inc_y:
                    # 2-column data - only Least Squares is appropriate
                    if "odr" in selected_method.lower():
                        messagebox.showwarning( 
                            get_string("curve_fitting", "warning", self.language),
                            get_string(
                                "curve_fitting",
                                "data_no_uncertainties_warning",
                                self.language,
                            ),
                        )
                        self.ui_builder.fitting_method_var.set(
                            get_string(
                                "curve_fitting", "least_squares_method", self.language
                            )
                        )
                elif has_inc_x and "least_squares" in selected_method.lower():
                    # 4-column data with Least Squares - warn that inc_x will be ignored
                    messagebox.showwarning(
                        get_string("curve_fitting", "warning", self.language),
                        get_string(
                            "curve_fitting",
                            "least_squares_ignores_inc_x",
                            self.language,
                        ),
                    )

    def get_selected_fitting_method(self) -> str:
        """Get the currently selected fitting method"""
        if self.ui_builder and hasattr(self.ui_builder, "fitting_method_var"):
            method_text = self.ui_builder.fitting_method_var.get()
            if get_string("curve_fitting", "odr_method", self.language) in method_text:
                return "odr"
            elif (
                get_string("curve_fitting", "least_squares_method", self.language)
                in method_text
            ):
                return "least_squares"
            elif (
                get_string("curve_fitting", "robust_method", self.language)
                in method_text
            ):
                return "robust"
            elif (
                get_string("curve_fitting", "bootstrap_method", self.language)
                in method_text
            ):
                return "bootstrap"
            elif (
                get_string("curve_fitting", "bayesian_method", self.language)
                in method_text
            ):
                return "bayesian"
        return "odr"  # Default fallback

    def update_fitting_method_visibility(self) -> None:
        """Update visibility/availability of fitting method dropdown based on data"""
        if (
            self.ui_builder
            and hasattr(self.ui_builder, "fitting_method_selector")
            and self.ui_builder.fitting_method_selector
        ):
            if hasattr(self, "sigma_x") and hasattr(self, "sigma_y"):
                has_inc_x = not np.allclose(self.sigma_x, 0)
                has_inc_y = not np.allclose(self.sigma_y, 0)

                if not has_inc_y:
                    # 2-column data (x, y) - no uncertainties, only Least Squares makes sense
                    self.ui_builder.fitting_method_selector.config(state="disabled")
                    self.ui_builder.fitting_method_var.set(
                        get_string(
                            "curve_fitting", "least_squares_method", self.language
                        )
                    )
                elif has_inc_x:
                    # 4-column data (x, inc_x, y, inc_y) - both methods available, default to ODR
                    self.ui_builder.fitting_method_selector.config(state="readonly")
                    self.ui_builder.fitting_method_var.set(
                        get_string("curve_fitting", "odr_method", self.language)
                    )
                else:
                    # 3-column data (x, y, inc_y) - both methods available, default to Least Squares
                    self.ui_builder.fitting_method_selector.config(state="readonly")
                    current = self.ui_builder.fitting_method_var.get()
                    if not current:
                        self.ui_builder.fitting_method_var.set(
                            get_string(
                                "curve_fitting", "least_squares_method", self.language
                            )
                        )
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
            results_header = get_string(
                "curve_fitting", "fit_results_header", self.language
            )
            self.results_text.insert(tk.END, f"{results_header}\n{'='*50}\n\n")

            # Display equation
            if hasattr(self, "equacao") and self.equacao:
                equation_label = get_string(
                    "curve_fitting", "equation_label", self.language
                )
                self.results_text.insert(
                    tk.END, f"{equation_label}: {self.equacao}\n\n"
                )

            # Display parameter values and uncertainties
            if hasattr(resultado, "beta") and hasattr(resultado, "sd_beta"):
                params_header = get_string(
                    "curve_fitting", "parameters_header", self.language
                )
                self.results_text.insert(tk.END, f"{params_header}:\n")

                beta_values = resultado.beta
                sd_beta_values = getattr(resultado, "sd_beta", None)

                if hasattr(self, "parametros") and self.parametros:
                    for i, param in enumerate(self.parametros):
                        if i < len(beta_values):
                            param_value = beta_values[i]
                            if sd_beta_values is not None and i < len(sd_beta_values):
                                param_error = sd_beta_values[i]
                                self.results_text.insert(
                                    tk.END,
                                    f"  {param} = {param_value:.6f} ± {param_error:.6f}\n",
                                )
                            else:
                                self.results_text.insert(
                                    tk.END, f"  {param} = {param_value:.6f}\n"
                                )
                else:
                    # Fallback if parameters list is not available
                    for i, value in enumerate(beta_values):
                        if sd_beta_values is not None and i < len(sd_beta_values):
                            error = sd_beta_values[i]
                            self.results_text.insert(
                                tk.END, f"  p{i} = {value:.6f} ± {error:.6f}\n"
                            )
                        else:
                            self.results_text.insert(tk.END, f"  p{i} = {value:.6f}\n")

                self.results_text.insert(tk.END, "\n")

            # Display covariance matrix if available
            if hasattr(resultado, "cov_beta") and resultado.cov_beta is not None:
                cov_beta = resultado.cov_beta
                # Check if covariance matrix is valid (not all zeros)
                if isinstance(cov_beta, np.ndarray) and not np.allclose(cov_beta, 0):
                    covariance_header = get_string(
                        "curve_fitting",
                        "covariance_matrix_header",
                        self.language,
                        fallback="Covariance Matrix",
                    )
                    self.results_text.insert(tk.END, f"{covariance_header}:\n")

                    # Display covariance matrix in a formatted way
                    n_params = cov_beta.shape[0]

                    # Header row with parameter names
                    header_row = "      "
                    if hasattr(self, "parametros") and self.parametros:
                        for i, param in enumerate(self.parametros[:n_params]):
                            # Convert to string to avoid formatting issues with Symbol objects
                            param_str = str(param)
                            header_row += f"{param_str:>12s} "
                    else:
                        for i in range(n_params):
                            header_row += f"{'p'+str(i):>12s} "
                    self.results_text.insert(tk.END, header_row + "\n")

                    # Matrix rows
                    for i in range(n_params):
                        if (
                            hasattr(self, "parametros")
                            and self.parametros
                            and i < len(self.parametros)
                        ):
                            # Convert to string to avoid formatting issues
                            row_label = str(self.parametros[i])
                        else:
                            row_label = f"p{i}"
                        # Limit row label to 5 characters
                        row_label = row_label[:5]
                        row_text = f"{row_label:>5s} "
                        for j in range(n_params):
                            row_text += f"{cov_beta[i, j]:>12.6e} "
                        self.results_text.insert(tk.END, row_text + "\n")

                    self.results_text.insert(tk.END, "\n")
            # Display goodness of fit statistics
            statistics_header = get_string(
                "curve_fitting", "statistics_header", self.language
            )
            self.results_text.insert(tk.END, f"{statistics_header}:\n")

            if hasattr(self, "last_chi2"):
                chi2_label = get_string("curve_fitting", "chi_squared", self.language)
                self.results_text.insert(
                    tk.END, f"  {chi2_label}: {self.last_chi2:.4f}\n"
                )

                # Reduced chi-squared if we have degrees of freedom info
                if (
                    hasattr(self, "x")
                    and hasattr(self, "parametros")
                    and self.parametros
                ):
                    dof = len(self.x) - len(self.parametros)
                    if dof > 0:
                        reduced_chi2 = self.last_chi2 / dof
                        reduced_chi2_label = get_string(
                            "curve_fitting", "reduced_chi_squared", self.language
                        )
                        self.results_text.insert(
                            tk.END, f"  {reduced_chi2_label}: {reduced_chi2:.4f}\n"
                        )

            if hasattr(self, "last_r2"):
                r2_label = get_string("curve_fitting", "r_squared", self.language)
                self.results_text.insert(tk.END, f"  {r2_label}: {self.last_r2:.4f}\n")

            # Display fitting method used
            fitting_method = self.get_selected_fitting_method()
            method_label = get_string(
                "curve_fitting", "fitting_method_used", self.language
            )

            # Map fitting method to translation key
            method_key_map = {
                "odr": "odr_method",
                "least_squares": "least_squares_method",
                "robust": "robust_method",
                "bootstrap": "bootstrap_method",
                "bayesian": "bayesian_method",
            }
            method_key = method_key_map.get(fitting_method, "odr_method")
            method_name = get_string("curve_fitting", method_key, self.language)
            self.results_text.insert(tk.END, f"  {method_label}: {method_name}\n")

        except Exception as e:
            # If there's an error displaying results, show a basic error message
            error_msg = get_string("curve_fitting", "display_error", self.language)
            self.results_text.insert(tk.END, f"{error_msg}: {str(e)}\n")

    def on_tab_activated(self):
        """Handle tab activation event"""
        """Called when this tab becomes active"""
        # Redraw plots if needed
        if hasattr(self, "plot_manager") and self.plot_manager:
            if hasattr(self.plot_manager, "canvas"):
                self.plot_manager.canvas.draw()

    def show_advanced_config(self):
        """Show the advanced configuration dialog"""
        self.advanced_config_dialog.show_dialog()

    def update_selection_mode(
        self, selection_mode: str
    ):  # Added type hint for selection_mode
        """Update the selection mode for adjustment points

        Args:
            selection_mode: The selection mode ('Todos', 'Selecionados', or 'Faixa')
        """
        # Store the selection mode
        if not hasattr(self, "adjustment_points_selection_mode"):
            self.adjustment_points_selection_mode = selection_mode
        else:
            self.adjustment_points_selection_mode = selection_mode

        # Update any UI elements if needed

    def update_adjustment_points(self, selected_indices: List[int]):
        """Update the selected adjustment points

        Args:
            selected_indices: List of indices of selected points
        """  # Store the selected indices
        self.selected_point_indices = selected_indices

    def update_fit_with_current_points(self):
        """Update the fit using currently selected points"""
        if hasattr(self, "last_result") and self.last_result is not None:
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
        if hasattr(self.ui_builder, "title_var"):
            self.ui_builder.title_var.set("")
        if self.file_entry:
            self.file_entry.delete(0, tk.END)

        # Reset variables
        if self.x_label_var:
            self.x_label_var.set("X")
        if self.y_label_var:
            self.y_label_var.set("Y")
            # Clear plot
        if hasattr(self, "plot_manager") and self.plot_manager:
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
        if hasattr(self, "ui_builder") and self.ui_builder:
            self.ui_builder.update_theme()

        # Update custom function manager tree view colors
        if hasattr(self, "custom_function_manager") and self.custom_function_manager:
            from app_files.utils.theme_manager import theme_manager

            if (
                hasattr(self.custom_function_manager, "functions_tree")
                and self.custom_function_manager.functions_tree
            ):
                try:
                    self.custom_function_manager.functions_tree.tag_configure(
                        "enabled",
                        foreground=theme_manager.get_adaptive_color("foreground"),
                    )
                    self.custom_function_manager.functions_tree.tag_configure(
                        "disabled",
                        foreground=theme_manager.get_adaptive_color("text_muted"),
                    )
                except tk.TclError:
                    pass

    def switch_language(self, language: str) -> None:
        """Update language for this component and refresh all UI text elements"""
        logging.info(f"AjusteCurvaFrame.switch_language called: {language}")
        self.language = language

        # Update window title if parent is a window
        if isinstance(self.parent, (tk.Tk, tk.Toplevel)):
            title = get_string("curve_fitting", "curve_fitting_title", self.language)
            self.parent.title(title)
            logging.debug("Updated parent title")

        # Update all UI text elements without destroying/recreating the interface
        logging.debug("Updating LabelFrames...")

        # Update top-level LabelFrames
        if hasattr(self.ui_builder, "control_frame") and self.ui_builder.control_frame:
            text = get_string(
                "curve_fitting", "controls", self.language, fallback="Controles"
            )
            self.ui_builder.control_frame.config(text=text)
            logging.debug(f"Updated control_frame: {text}")

        if (
            hasattr(self.ui_builder, "plot_area_frame")
            and self.ui_builder.plot_area_frame
        ):
            text = get_string(
                "curve_fitting", "plot", self.language, fallback="Gráfico"
            )
            self.ui_builder.plot_area_frame.config(text=text)
            logging.debug(f"Updated plot_area_frame: {text}")

        # Update data input frames
        if hasattr(self.ui_builder, "data_frame") and self.ui_builder.data_frame:
            text = get_string(
                "curve_fitting",
                "data_input",
                self.language,
                fallback="Entrada de dados",
            )
            self.ui_builder.data_frame.config(text=text)
            logging.debug(f"Updated data_frame: {text}")

        if hasattr(self.ui_builder, "preview_frame") and self.ui_builder.preview_frame:
            text = get_string(
                "curve_fitting",
                "loaded_data",
                self.language,
                fallback="Dados carregados",
            )
            self.ui_builder.preview_frame.config(text=text)
            logging.debug(f"Updated preview_frame: {text}")

        # Update LabelFrame texts
        if hasattr(self.ui_builder, "params_frame") and self.ui_builder.params_frame:
            text = get_string(
                "curve_fitting",
                "fitting_parameters",
                self.language,
                fallback="Parâmetros de ajuste",
            )
            self.ui_builder.params_frame.config(text=text)
            logging.debug(f"Updated params_frame: {text}")
        else:
            logging.warning("params_frame not found!")

        if (
            hasattr(self.ui_builder, "graph_settings_frame")
            and self.ui_builder.graph_settings_frame
        ):
            text = get_string(
                "curve_fitting",
                "graph_settings",
                self.language,
                fallback="Configurações do gráfico",
            )
            self.ui_builder.graph_settings_frame.config(text=text)
            logging.debug(f"Updated graph_settings_frame: {text}")

        if hasattr(self.ui_builder, "actions_frame") and self.ui_builder.actions_frame:
            self.ui_builder.actions_frame.config(
                text=get_string("curve_fitting", "actions", self.language)
            )

        if hasattr(self.ui_builder, "fitting_frame") and self.ui_builder.fitting_frame:
            text = get_string(
                "curve_fitting", "progress", self.language, fallback="Progresso"
            )
            self.ui_builder.fitting_frame.config(text=text)

        if hasattr(self.ui_builder, "results_frame") and self.ui_builder.results_frame:
            text = get_string(
                "curve_fitting", "results", self.language, fallback="Resultados"
            )
            self.ui_builder.results_frame.config(text=text)

        # Update labels by finding them in the UI hierarchy
        logging.debug("Updating labels...")
        self._update_labels_in_frame()

        # Update buttons
        logging.debug("Updating buttons...")
        self._update_buttons()

        # Update combobox values
        logging.debug("Updating comboboxes...")
        self._update_comboboxes()

        # Update child managers
        logging.debug("Updating child managers...")
        self._update_child_managers(language)

        logging.info("AjusteCurvaFrame.switch_language completed")

    def _update_labels_in_frame(self) -> None:
        """Update all labels in the parameter and graph settings frames"""
        if (
            not hasattr(self.ui_builder, "params_frame")
            or not self.ui_builder.params_frame
        ):
            return

        # Update parameter frame labels
        for child in self.ui_builder.params_frame.winfo_children():
            if isinstance(child, tk.Frame) or isinstance(
                child, ttk.Frame
            ):  # left_params_frame or num_settings_frame
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Label):
                        self._update_label_text(subchild)

        # Update graph settings labels
        if (
            hasattr(self.ui_builder, "graph_settings_frame")
            and self.ui_builder.graph_settings_frame
        ):
            for child in self.ui_builder.graph_settings_frame.winfo_children():
                if isinstance(child, ttk.Label):
                    self._update_label_text(child)
                elif isinstance(child, tk.Frame) or isinstance(
                    child, ttk.Frame
                ):  # scales_frame
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Label):
                            self._update_label_text(subchild)

        # Update data input labels (file label, format label) and buttons
        if hasattr(self.ui_builder, "data_frame") and self.ui_builder.data_frame:
            for child in self.ui_builder.data_frame.winfo_children():
                # frames like file_input_frame or format_frame
                if isinstance(child, tk.Frame) or isinstance(child, ttk.Frame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Label):
                            self._update_label_text(subchild)
                        elif isinstance(subchild, ttk.Button):
                            self._update_button_text(subchild)
                elif isinstance(child, ttk.Label):
                    self._update_label_text(child)

    def _update_label_text(self, label: tk.Label) -> None:
        """Update a single label's text based on its current content"""
        current_text = label.cget("text")

        # Map translation keys to check against both languages
        label_mappings = [
            ("curve_fitting", "model"),
            ("curve_fitting", "equation"),
            ("curve_fitting", "fitting_method"),
            ("curve_fitting", "max_iterations"),
            ("curve_fitting", "num_points"),
            ("curve_fitting", "title"),
            ("curve_fitting", "x_label"),
            ("curve_fitting", "y_label"),
            ("curve_fitting", "x_scale"),
            ("curve_fitting", "y_scale"),
        ]

        # Check if current text matches any translation in any language
        for section, key in label_mappings:
            # Check against Portuguese text
            pt_text = get_string(section, key, "pt", fallback="")
            # Check against English text
            en_text = get_string(section, key, "en", fallback="")

            if current_text in [pt_text, en_text]:
                # Update to the new language
                new_text = get_string(
                    section, key, self.language, fallback=current_text
                )
                label.config(text=new_text)
                logging.debug(f"Updated label '{current_text}' -> '{new_text}'")
                break
        else:
            # Label didn't match any mapping
            logging.debug(f"Label text '{current_text}' didn't match any mapping")

    def _update_buttons(self) -> None:
        """Update all button texts"""
        # Update action buttons
        if hasattr(self.ui_builder, "actions_frame") and self.ui_builder.actions_frame:
            for child in self.ui_builder.actions_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    self._update_button_text(child)

        # Update buttons in params frame (More Configs, Help)
        if hasattr(self.ui_builder, "params_frame") and self.ui_builder.params_frame:
            for child in self.ui_builder.params_frame.winfo_children():
                if isinstance(child, tk.Frame) or isinstance(
                    child, ttk.Frame
                ):  # buttons_frame
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Button):
                            self._update_button_text(subchild)

    def _update_button_text(self, button: tk.Button) -> None:
        """Update a single button's text based on its command"""
        command_str = str(button.cget("command"))

        # Map commands to translation keys
        if "perform_fit" in command_str:
            button.config(
                text=get_string("curve_fitting", "perform_fit", self.language)
            )
        elif "save_graph" in command_str:
            button.config(text=get_string("curve_fitting", "save_graph", self.language))
        elif "clear_all_data" in command_str:
            button.config(text=get_string("curve_fitting", "clear_all", self.language))
        elif "show_advanced_config" in command_str:
            button.config(
                text=get_string("curve_fitting", "more_configs", self.language)
            )
        elif "show_model_help" in command_str:
            text = get_string(
                "curve_fitting", "help_models", self.language, fallback="Ajuda"
            )
            button.config(text=text)
        elif "browse_file" in command_str:
            button.config(text=get_string("curve_fitting", "browse", self.language))
        elif "show_format_override_dialog" in command_str:
            # Gear button uses an icon; update tooltip text if UIBuilder stored it
            try:
                if hasattr(self, "ui_builder") and getattr(self.ui_builder, "reinterpret_tooltip", None) is not None:
                    # Hovertip does not expose a public API to change text reliably, but if available, set attribute
                    try:
                        # Some Hovertip implementations accept .text or _text attribute
                        setattr(self.ui_builder.reinterpret_tooltip, "text", get_string("curve_fitting", "swap_columns_tooltip", self.language))
                    except Exception:
                        pass
            except Exception:
                pass

    def _update_comboboxes(self) -> None:
        """Update all combobox values and current selections"""
        # Update fitting method selector
        if hasattr(self.ui_builder, "fitting_method_selector"):
            # Store the current method by checking against all languages
            current_method = self.ui_builder.fitting_method_selector.get()
            current_method_key = None

            # Map of method keys
            method_keys = [
                "odr_method",
                "least_squares_method",
                "robust_method",
                "bootstrap_method",
                "bayesian_method",
            ]

            # Find which method is currently selected
            for method_key in method_keys:
                pt_text = get_string("curve_fitting", method_key, "pt", fallback="")
                en_text = get_string("curve_fitting", method_key, "en", fallback="")
                if current_method in [pt_text, en_text]:
                    current_method_key = method_key
                    break

            # Update the values list
            self.ui_builder.fitting_method_selector["values"] = [
                get_string(
                    "curve_fitting", "odr_method", self.language, fallback="ODR"
                ),
                get_string(
                    "curve_fitting",
                    "least_squares_method",
                    self.language,
                    fallback="Mínimos Quadrados",
                ),
                get_string(
                    "curve_fitting", "robust_method", self.language, fallback="Robusto"
                ),
                get_string(
                    "curve_fitting",
                    "bootstrap_method",
                    self.language,
                    fallback="Bootstrap",
                ),
                get_string(
                    "curve_fitting",
                    "bayesian_method",
                    self.language,
                    fallback="Bayesiano",
                ),
            ]

            # Update the current selection if we found it
            if current_method_key:
                new_text = get_string(
                    "curve_fitting", current_method_key, self.language
                )
                self.ui_builder.fitting_method_selector.set(new_text)

        # Update scale comboboxes
        for scale_attr in ["x_scale", "y_scale"]:
            if hasattr(self.ui_builder, scale_attr):
                scale_combo = getattr(self.ui_builder, scale_attr)
                scale_combo["values"] = [
                    get_string(
                        "curve_fitting", "linear", self.language, fallback="Linear"
                    ),
                    get_string(
                        "curve_fitting", "log", self.language, fallback="Logarítmica"
                    ),
                ]
                # Update current value if it's set
                current_value = scale_combo.get()
                if current_value:
                    # Check against both languages
                    linear_pt = get_string(
                        "curve_fitting", "linear", "pt", fallback="Linear"
                    )
                    linear_en = get_string(
                        "curve_fitting", "linear", "en", fallback="Linear"
                    )
                    log_pt = get_string(
                        "curve_fitting", "log", "pt", fallback="Logarítmica"
                    )
                    log_en = get_string(
                        "curve_fitting", "log", "en", fallback="Logarithmic"
                    )

                    if current_value in [linear_pt, linear_en]:
                        new_value = get_string(
                            "curve_fitting",
                            "linear",
                            self.language,
                            fallback=current_value,
                        )
                        scale_combo.set(new_value)
                    elif current_value in [log_pt, log_en]:
                        new_value = get_string(
                            "curve_fitting",
                            "log",
                            self.language,
                            fallback=current_value,
                        )
                        scale_combo.set(new_value)

        # Update save graph options
        if hasattr(self.ui_builder, "results_frame") and self.ui_builder.results_frame:
            for child in self.ui_builder.results_frame.winfo_children():
                if isinstance(child, tk.Frame):  # buttons_frame
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Frame):  # save_frame
                            for subsubchild in subchild.winfo_children():
                                if isinstance(subsubchild, tk.ttk.Combobox):
                                    self._update_save_options_combobox(subsubchild)

    def _update_save_options_combobox(self, combobox: tk.ttk.Combobox) -> None:
        """Update save options combobox values and current selection"""
        save_options = [
            ("full", get_string("curve_fitting", "full_graph", self.language)),
            (
                "fit_and_data",
                get_string("curve_fitting", "fit_and_data", self.language),
            ),
            ("only_data", get_string("curve_fitting", "only_data", self.language)),
            ("only_fit", get_string("curve_fitting", "only_fit", self.language)),
            (
                "only_residuals",
                get_string("curve_fitting", "only_residuals", self.language),
            ),
        ]
        combobox["values"] = [option[1] for option in save_options]

        # Update current display text
        current_index = combobox.current()
        if current_index >= 0 and current_index < len(save_options):
            combobox.set(save_options[current_index][1])

    def _update_child_managers(self, language: str) -> None:
        """Update language in child managers"""
        # Update parameter estimates manager
        if hasattr(self, "parameter_estimates_manager") and hasattr(
            self.parameter_estimates_manager, "switch_language"
        ):
            self.parameter_estimates_manager.switch_language(language)

        # Update history manager
        if hasattr(self, "history_manager") and hasattr(
            self.history_manager, "switch_language"
        ):
            self.history_manager.switch_language(language)

        # Update plot manager (axis labels and legend)
        if hasattr(self, "plot_manager") and hasattr(self.plot_manager, "switch_language"):
            try:
                self.plot_manager.switch_language(language)
            except Exception:
                pass

        # Update model manager language
        if hasattr(self, "model_manager"):
            self.model_manager.language = language

        # Update adjustment points manager
        if hasattr(self, "adjustment_points_manager") and hasattr(
            self.adjustment_points_manager, "switch_language"
        ):
            self.adjustment_points_manager.switch_language(language)

        # Ensure advanced config dialog uses new language next time it's shown
        if hasattr(self, "advanced_config_dialog"):
            try:
                self.advanced_config_dialog.language = language
            except Exception:
                pass
