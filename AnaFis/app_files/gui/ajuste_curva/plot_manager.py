"""Plot manager for curve fitting"""

import logging
import numpy as np
from numpy.typing import NDArray
import sympy as sp
from typing import TYPE_CHECKING, Optional, List, Callable, cast, Sequence, Any, Dict
import re

from app_files.utils.translations.api import get_string

# Type aliases for better type annotation
BetaArray = NDArray[np.float64]
FloatArray = NDArray[np.float64]


SUPPORTED_SYMPY_OBJECTS: Dict[str, Any] = {
    # Basic trigonometric functions
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "cot": sp.cot,
    "sec": sp.sec,
    "csc": sp.csc,
    # Inverse trigonometric functions
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "acot": sp.acot,
    "asec": sp.asec,
    "acsc": sp.acsc,
    "arcsin": sp.asin,
    "arccos": sp.acos,
    "arctan": sp.atan,
    "arccot": sp.acot,
    "arcsec": sp.asec,
    "arccsc": sp.acsc,
    # Hyperbolic functions
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "coth": sp.coth,
    "sech": sp.sech,
    "csch": sp.csch,
    # Inverse hyperbolic functions
    "asinh": sp.asinh,
    "acosh": sp.acosh,
    "atanh": sp.atanh,
    "acoth": sp.acoth,
    "arcsinh": sp.asinh,
    "arccosh": sp.acosh,
    "arctanh": sp.atanh,
    "arccoth": sp.acoth,  # Exponential and logarithmic functions
    "exp": sp.exp,
    "log": sp.log,
    "log10": lambda x: sp.log(x, 10),
    "log2": lambda x: sp.log(x, 2),
    "ln": sp.log,
    "logb": lambda x, b: sp.log(
        x, b
    ),  # logarithm with any base: logb(x, base)
    # Power and root functions
    "sqrt": sp.sqrt,
    "cbrt": sp.cbrt,
    "pow": sp.Pow,
    "square": lambda x: x**2,
    # Rounding and integer functions
    "abs": sp.Abs,
    "sign": sp.sign,
    "floor": sp.floor,
    "ceil": sp.ceiling,
    # Special mathematical functions
    "gamma": sp.gamma,
    "factorial": sp.factorial,
    "erf": sp.erf,
    "erfc": sp.erfc,
    # Step and discontinuous functions
    "heaviside": sp.Heaviside,
    # Piecewise functions
    "piecewise": sp.Piecewise,
    # Constants
    "pi": sp.pi,
    "e": sp.E,
    "inf": sp.oo,
    "infinity": sp.oo,
}


def preprocess_implicit_multiplication(expression: str) -> str:
    """
    Preprocess mathematical expressions to handle implicit multiplication.

    Converts patterns like:
    - 3x -> 3*x
    - 2sin(x) -> 2*sin(x)
    - (x+1)(x-1) -> (x+1)*(x-1)
    - x(x+1) -> x*(x+1)
    - 2(x+1) -> 2*(x+1)
    Args:
        expression: The mathematical expression string

    Returns:
        The expression with explicit multiplication operators and SymPy function references
    """
    if not expression:
        return expression

    # Remove spaces for easier processing
    expr = expression.replace(" ", "")

    # Step 1: Replace ^ with ** for power operations
    expr = expr.replace("^", "**")

    # Step 2: Handle implicit multiplication before function substitution
    # This avoids conflicts with the sp. prefixes
    math_functions = list(SUPPORTED_SYMPY_OBJECTS.keys())

    # Pattern 1: Number followed by function name (e.g., 2sin, 3cos)
    # Sort functions by length (longest first) to handle overlapping names correctly
    sorted_functions = sorted(math_functions, key=len, reverse=True)
    for func in sorted_functions:
        expr = re.sub(rf"(\d)({func})\b", r"\1*\2", expr)
    # Pattern 2: Number followed by variable (e.g., 3x, 2y)
    # Look for digit followed by single letter that's not a function name
    function_pattern = r"\b(?:" + "|".join(sorted_functions) + r")\b"
    expr = re.sub(rf"(\d)([a-zA-Z])(?!" + function_pattern + r")", r"\1*\2", expr)

    # Pattern 3: Single variable followed by opening parenthesis (e.g., x(, y()
    # But not function names - be very specific: single letter variables only
    expr = re.sub(r"(\b[a-zA-Z]\b)(?!" + function_pattern + r")\(", r"\1*(", expr)

    # Pattern 4: Closing parenthesis followed by opening parenthesis (e.g., )(
    expr = re.sub(r"\)\(", r")*(", expr)

    # Pattern 5: Closing parenthesis followed by letter or number (e.g., )x, )2
    expr = re.sub(r"\)([a-zA-Z0-9])", r")*\1", expr)
    # Pattern 6: Number followed by opening parenthesis (e.g., 2(, 3()
    expr = re.sub(r"(\d)\(", r"\1*(", expr)

    # Pattern 7: Function followed by function (e.g., sin(x)cos(x))
    # This handles cases like sin(x)cos(x) -> sin(x)*cos(x)
    expr = re.sub(rf"(\))((?:" + "|".join(sorted_functions) + r")\b)", r"\1*\2", expr)

    return expr


if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from scipy.odr import Output
    # Import CustomFunction for type annotations
    from .models import CustomFunction

    # If ModelCallable is defined elsewhere and imported, use that.
    # Otherwise, define it or use its structure directly.
    # from .model_manager import ModelCallable # Assuming it's accessible
    # For now, let's use the direct structure for model_func
    ModelCallable = Callable[
        [Sequence[float], NDArray[np.float64]], NDArray[np.float64]
    ]  # Reverted to use Sequence


class PlotManager:
    """Handles plotting data and fit results for curve fitting"""

    fig: "Figure"
    ax: "Axes"
    ax_res: "Axes"
    canvas: "FigureCanvasTkAgg"
    language: str

    def __init__(
        self,
        fig: "Figure",
        ax: "Axes",
        ax_res: "Axes",
        canvas: "FigureCanvasTkAgg",
        language: str = "pt",
    ) -> None:
        """Initialize the plot manager

        Args:
            fig: Matplotlib figure
            ax: Main axis for plotting
            ax_res: Residuals axis
            canvas: Matplotlib canvas for displaying plots
            language: Current language ('pt' or 'en')
        """
        self.fig = fig
        self.ax = ax
        self.ax_res = ax_res
        self.canvas = canvas
        self.language = language

    def _get_translation(self, key: str, fallback: str = "") -> str:
        """Get translation for a given key using the correct API signature"""
        return get_string("ajuste_curva", key, self.language, fallback)

    def initialize_empty_plot(self) -> None:
        """Initialize an empty plot"""
        self.ax.clear()
        self.ax_res.clear()

        # Add grid to main plot and residuals
        self.ax.grid(True, linestyle="--", alpha=0.7)
        self.ax_res.grid(True, linestyle="--", alpha=0.7)
        # Default labels using translations
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax_res.set_xlabel("X")
        self.ax_res.set_ylabel(self._get_translation("residuals", fallback="Residuals"))
        # Ensure tight layout
        self.fig.tight_layout()
        self.canvas.draw()
    def plot_data_only(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64],
        sigma_x: Optional[NDArray[np.float64]],
        sigma_y: Optional[NDArray[np.float64]],
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        title: Optional[str] = None,
        x_scale: str = "linear",
        y_scale: str = "linear",
    ) -> None:
        """Plot only the data points without fit curve

        Args:
            x: X data
            y: Y data
            sigma_x: X uncertainties
            sigma_y: Y uncertainties
            x_label: X-axis label
            y_label: Y-axis label
            title: Plot title
            x_scale: X-axis scale ('linear' or 'log')
            y_scale: Y-axis scale ('linear' or 'log')
        """
        self.ax.clear()
        self.ax_res.clear()

        # Plot data with error bars using translated label
        self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt="o", capsize=3, label=self._get_translation("data_label", fallback="Data"))
        # Set scales
        self.ax.set_xscale(x_scale)
        self.ax.set_yscale(y_scale)
        self.ax_res.set_xscale(x_scale)
        # Set labels
        if x_label:
            self.ax.set_xlabel(x_label)
            self.ax_res.set_xlabel(x_label)
        if y_label:
            self.ax.set_ylabel(y_label)
        if title:
            self.ax.set_title(title)
        # Default residuals label using translation
        self.ax_res.set_ylabel(self._get_translation("residuals", fallback="Residuals"))
        # Add grid to both plots
        self.ax.grid(True, linestyle="--", alpha=0.7)
        self.ax_res.grid(True, linestyle="--", alpha=0.7)
        # Add legend
        self.ax.legend()
        # Ensure tight layout
        self.fig.tight_layout()
        self.canvas.draw()
    def plot_fit_results(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64],
        sigma_x: Optional[NDArray[np.float64]],
        sigma_y: Optional[NDArray[np.float64]],
        model_func: "ModelCallable",  # Or Callable[[Sequence[float], NDArray[np.float64]], NDArray[np.float64]]
        result: "Output",
        chi2: float,
        r2: float,
        equation: str,
        parameters: List[sp.Symbol],
        num_points: int = 1000,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        title: Optional[str] = None,
        x_scale: str = "linear",
        y_scale: str = "linear",
    ) -> None:
        """Plot fit results with data and residuals

        Args:
            x: X data
            y: Y data
            sigma_x: X uncertainties
            sigma_y: Y uncertainties
            model_func: Fitted model function
            result: Fit result object
            chi2: Chi-squared value
            r2: R-squared value
            equation: Equation string
            parameters: List of parameters
            num_points: Number of points for fit curve
            x_label: X-axis label
            y_label: Y-axis label
            title: Plot title
            x_scale: X-axis scale ('linear' or 'log')
            y_scale: Y-axis scale ('linear' or 'log')
        """
        self.ax.clear()
        self.ax_res.clear()

        # Generate x values for plotting the fit curve
        x_fit: NDArray[np.float64]
        if x_scale == "log":
            # For log scale, use logarithmically spaced points
            x_min_val, x_max_val = np.min(x), np.max(x)
            if x_min_val <= 0:
                positive_x = x[x > 0]
                if positive_x.size > 0:
                    x_min_val = np.min(positive_x)  # Find smallest positive value
                else:  # All values are <=0, log scale is problematic. Fallback or raise error.                    
                    # Fallback to linear for safety, or handle as error
                    x_fit = np.linspace(x_min_val, x_max_val, num_points).astype(
                        np.float64
                    )
                    logging.warning(
                        "Log scale requested for non-positive data. Using linear scale for fit curve."
                    )
                    # Alternatively, could raise ValueError("Cannot use log scale with non-positive data.")
            if (
                x_min_val > 0 and x_max_val > 0
            ):  # Ensure min and max are positive for logspace
                x_fit = np.logspace(
                    np.log10(x_min_val),
                    np.log10(x_max_val),
                    num_points,
                    dtype=np.float64,
                )
            else:  # Fallback if still problematic after trying to find positive min
                x_fit = np.linspace(np.min(x), np.max(x), num_points).astype(np.float64)

        else:
            # For linear scale, use linearly spaced points
            x_fit = np.linspace(np.min(x), np.max(x), num_points).astype(np.float64)
        # Calculate y values using the model function
        try:  # Type annotation for beta array from ODR result
            beta_params = cast(BetaArray, result.beta)
            # Use model function to generate fit line
            y_fit = model_func(cast(Sequence[float], beta_params), x_fit)
            y_model = model_func(cast(Sequence[float], beta_params), x)

            # Calculate residuals
            residuals = y - y_model

            # Plot data with error bars using translated label
            self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt="o", capsize=3, label=self._get_translation("data_label", fallback="Data"))
            self.ax.plot(x_fit, y_fit, "-", label=self._get_translation("fit_label", fallback="Fit"))
            # Plot residuals
            self.ax_res.errorbar(x, residuals, yerr=sigma_y, fmt="o", capsize=3)
            self.ax_res.axhline(y=0, color="r", linestyle="-", alpha=0.3)
            # Set scales
            self.ax.set_xscale(x_scale)
            self.ax.set_yscale(y_scale)
            self.ax_res.set_xscale(x_scale)
            # Set labels
            if x_label:
                self.ax.set_xlabel(x_label)
                self.ax_res.set_xlabel(x_label)
            if y_label:
                self.ax.set_ylabel(y_label)
            if title:
                self.ax.set_title(title)
            else:  # Create title from equation if not provided using translated prefix
                eq_title = equation
                beta_values = cast(BetaArray, result.beta)
                for i, p_sym in enumerate(parameters):
                    eq_title = eq_title.replace(
                        str(p_sym), f"{str(p_sym)}={beta_values[i]:.4f}"
                    )
                self.ax.set_title(f"{self._get_translation('fit_title_prefix', fallback='Fit:')} {eq_title}")
            # Residuals label using translation
            self.ax_res.set_ylabel(self._get_translation("residuals", fallback="Residuals"))
            # Add grid to both plots
            self.ax.grid(True, linestyle="--", alpha=0.7)
            self.ax_res.grid(True, linestyle="--", alpha=0.7)
            # Add fit statistics to legend
            self.ax.legend(title=f"χ²={chi2:.2f}, R²={r2:.4f}")
            # Ensure tight layout
            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            logging.error(f"Error in plot_fit_results: {str(e)}")
            # If fit plotting fails, at least show the data
            self.plot_data_only(
                x, y, sigma_x, sigma_y, x_label, y_label, title, x_scale, y_scale
            )

    def update_legend(self) -> None:
        """Updates the legend on the plot."""
        # Get current handles and labels
        handles, labels = self.ax.get_legend_handles_labels()
        # If there are no handles or labels, remove the legend completely
        if not handles and not labels:
            legend = self.ax.get_legend()
            if legend:
                legend.remove()
        else:
            # Create/update legend with current handles and labels
            self.ax.legend(handles, labels)
        # This method can be called after language change to update plot labels        pass

    def switch_language(self, language: str) -> None:
        """Switch language for plot labels and redraw canvas."""
        try:
            self.language = language
            # Update residuals ylabel
            try:
                self.ax_res.set_ylabel(self._get_translation("residuals", fallback="Residuals"))
            except Exception:
                pass
            # Optionally update data/fit legend labels if present
            try:
                handles, labels = self.ax.get_legend_handles_labels()
                # Replace known labels using translations if they match previous languages
                new_labels = []
                for lbl in labels:
                    if lbl in [get_string("ajuste_curva", "data_label", "pt"), get_string("ajuste_curva", "data_label", "en")]:
                        new_labels.append(self._get_translation("data_label", fallback="Data"))
                    elif lbl in [get_string("ajuste_curva", "fit_label", "pt"), get_string("ajuste_curva", "fit_label", "en")]:
                        new_labels.append(self._get_translation("fit_label", fallback="Fit"))
                    else:
                        new_labels.append(lbl)
                if new_labels:
                    self.ax.legend(handles=handles, labels=new_labels)
            except Exception:
                pass

            # Redraw
            try:
                self.fig.tight_layout()
                self.canvas.draw()
            except Exception:
                pass
        except Exception:
            logging.exception("Failed to switch language on PlotManager")

    def force_refresh(self) -> None:
        """Force refresh the plot canvas - used as a fallback for plot updates"""
        try:
            self.fig.tight_layout()
            self.canvas.draw()
            logging.debug("Force refresh completed successfully")
        except Exception as e:
            logging.error(f"Force refresh failed: {e}")

    def plot_custom_functions(self, custom_functions: List["CustomFunction"]) -> None:
        """Plot custom functions on the graph.

        Args:
            custom_functions: List of custom function objects to plot
        """
        import logging

        logging.debug(
            f"plot_custom_functions called with {len(custom_functions)} functions"
        )

        # Remove existing custom function lines first (regardless of whether we have new functions)
        lines_to_remove: List[Any] = []
        for line in self.ax.get_lines():
            if hasattr(line, "is_custom_function") and getattr(
                line, "is_custom_function", False
            ):
                lines_to_remove.append(line)

        logging.debug(f"Removing {len(lines_to_remove)} existing custom function lines")
        for line in lines_to_remove:
            line.remove()
        # If no functions to plot, just clear and return
        if not custom_functions:
            logging.debug("No custom functions to plot - clearing and updating")
            self.update_legend()
            self.canvas.draw()
            # Force immediate redraw instead of draw_idle
            return

        # Get current x range for plotting custom functions
        if self.ax.get_xlim():
            x_min, x_max = self.ax.get_xlim()
            x = np.linspace(x_min, x_max, 1000)
        else:
            # Default range if no data plotted yet
            x = np.linspace(-10, 10, 1000)
        # Symbol for the independent variable
        x_sym = sp.Symbol("x")

        for func in custom_functions:
            try:
                # Determine the plotting range for this specific function
                if func.x_min is not None and func.x_max is not None:
                    # Both limits specified - use custom range
                    x = np.linspace(func.x_min, func.x_max, 1000)
                elif func.x_min is not None:
                    # Only minimum specified - use custom min to axis max (or default)
                    if self.ax.get_xlim():
                        _, axis_max = self.ax.get_xlim()
                        x = np.linspace(func.x_min, axis_max, 1000)
                    else:
                        x = np.linspace(func.x_min, 10, 1000)  # Default max
                elif func.x_max is not None:
                    # Only maximum specified - use axis min (or default) to custom max
                    if self.ax.get_xlim():
                        axis_min, _ = self.ax.get_xlim()
                        x = np.linspace(axis_min, func.x_max, 1000)
                    else:
                        x = np.linspace(-10, func.x_max, 1000)  # Default min
                else:
                    # No custom range specified - use axis range or default
                    if self.ax.get_xlim():
                        x_min, x_max = self.ax.get_xlim()
                        x = np.linspace(x_min, x_max, 1000)
                    else:
                        x = np.linspace(-10, 10, 1000)  # Default range

                # Preprocess the expression to handle implicit multiplication
                preprocessed_expression = preprocess_implicit_multiplication(
                    func.func_text
                )
                # Parse the expression with the same comprehensive function dictionary
                local_dict = SUPPORTED_SYMPY_OBJECTS
                expr = sp.sympify(preprocessed_expression, locals=local_dict)
                # Convert to numeric function and evaluate
                func_lambda = sp.lambdify(x_sym, expr, modules=["numpy"])
                y = func_lambda(x)

                # Create label with range info if custom range is specified
                if func.x_min is not None or func.x_max is not None:
                    range_info = f" [{func.x_min or '∞'}, {func.x_max or '∞'}]"
                    label = f"f(x) = {func.func_text}{range_info}"
                else:
                    label = f"f(x) = {func.func_text}"
                # Plot the function
                (line,) = self.ax.plot(x, y, color=func.color, linestyle="--", label=label)
                # Add custom attribute to identify this as a custom function
                setattr(line, "is_custom_function", True)
            except Exception as e:
                # Log error but continue with other functions
                logging.error(f"Error plotting function {func.func_text}: {e}")
                continue

        # Update legend and redraw canvas
        self.update_legend()
        self.canvas.draw_idle()