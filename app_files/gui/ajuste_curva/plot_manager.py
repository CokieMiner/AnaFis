"""Plot manager for curve fitting"""
import numpy as np
from numpy.typing import NDArray
import sympy as sp
from typing import TYPE_CHECKING, Optional, List, Callable, cast, Sequence

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.legend import Legend as MplLegend
    from matplotlib.artist import Artist
    from matplotlib.lines import Line2D
    from scipy.odr import Output
    # If ModelCallable is defined elsewhere and imported, use that.
    # Otherwise, define it or use its structure directly.
    # from .model_manager import ModelCallable # Assuming it's accessible
    # For now, let's use the direct structure for model_func
    ModelCallable = Callable[[Sequence[float], NDArray[np.float64]], NDArray[np.float64]] # Reverted to use Sequence


class PlotManager:
    """Handles plotting data and fit results for curve fitting"""
    fig: 'Figure'
    ax: 'Axes'
    ax_res: 'Axes'
    canvas: 'FigureCanvasTkAgg'
    language: str
    
    def __init__(self, fig: 'Figure', ax: 'Axes', ax_res: 'Axes', canvas: 'FigureCanvasTkAgg', language: str ='pt') -> None:
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
        
    def set_language(self, language: str) -> None:
        """Set the language for plot labels
        
        Args:
            language: Language code ('pt' or 'en')
        """
        self.language = language
        
    def _get_translation(self, key: str) -> str:
        """Get translation for a given key
        
        Args:
            key: Translation key
            
        Returns:
            Translated string
        """
        return TRANSLATIONS.get(self.language, {}).get(key, key) # type: ignore[reportUnknownMemberType]
        
    def initialize_empty_plot(self) -> None:
        """Initialize an empty plot"""
        self.ax.clear()
        self.ax_res.clear()
        
        # Add grid to main plot and residuals
        self.ax.grid(True, linestyle='--', alpha=0.7) # type: ignore[reportUnknownMemberType]
        self.ax_res.grid(True, linestyle='--', alpha=0.7) # type: ignore[reportUnknownMemberType]
        
        # Default labels using translations
        self.ax.set_xlabel('X') # type: ignore[reportUnknownMemberType]
        self.ax.set_ylabel('Y') # type: ignore[reportUnknownMemberType]
        self.ax_res.set_xlabel('X') # type: ignore[reportUnknownMemberType]
        self.ax_res.set_ylabel(self._get_translation('residuals')) # type: ignore[reportUnknownMemberType]
        
        # Ensure tight layout
        self.fig.tight_layout() # type: ignore[reportUnknownMemberType]
        self.canvas.draw() # type: ignore[reportUnknownMemberType]
    
    def plot_data_only(self, 
                       x: NDArray[np.float64], 
                       y: NDArray[np.float64], 
                       sigma_x: Optional[NDArray[np.float64]], 
                       sigma_y: Optional[NDArray[np.float64]], 
                       x_label: Optional[str] = None, 
                       y_label: Optional[str] = None, 
                       title: Optional[str] = None, 
                       x_scale: str = 'linear', 
                       y_scale: str = 'linear') -> None:
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
        self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt='o', capsize=3, label=self._get_translation('data_label')) # type: ignore[reportUnknownMemberType]
        
        # Set scales
        self.ax.set_xscale(x_scale) # type: ignore[reportUnknownMemberType]
        self.ax.set_yscale(y_scale) # type: ignore[reportUnknownMemberType]
        self.ax_res.set_xscale(x_scale) # type: ignore[reportUnknownMemberType]
        
        # Set labels
        if x_label:
            self.ax.set_xlabel(x_label) # type: ignore[reportUnknownMemberType]
            self.ax_res.set_xlabel(x_label) # type: ignore[reportUnknownMemberType]
        if y_label:
            self.ax.set_ylabel(y_label) # type: ignore[reportUnknownMemberType]
        if title:
            self.ax.set_title(title) # type: ignore[reportUnknownMemberType]
        
        # Default residuals label using translation
        self.ax_res.set_ylabel(self._get_translation('residuals')) # type: ignore[reportUnknownMemberType]
        
        # Add grid to both plots
        self.ax.grid(True, linestyle='--', alpha=0.7) # type: ignore[reportUnknownMemberType]
        self.ax_res.grid(True, linestyle='--', alpha=0.7) # type: ignore[reportUnknownMemberType]
        
        # Add legend
        self.ax.legend() # type: ignore[reportUnknownMemberType]
        
        # Ensure tight layout
        self.fig.tight_layout() # type: ignore[reportUnknownMemberType]
        self.canvas.draw() # type: ignore[reportUnknownMemberType]
    
    def plot_fit_results(self, 
                        x: NDArray[np.float64], 
                        y: NDArray[np.float64], 
                        sigma_x: Optional[NDArray[np.float64]], 
                        sigma_y: Optional[NDArray[np.float64]], 
                        model_func: 'ModelCallable', # Or Callable[[Sequence[float], NDArray[np.float64]], NDArray[np.float64]]
                        result: 'Output', 
                        chi2: float, 
                        r2: float, 
                        equation: str, 
                        parameters: List[sp.Symbol], 
                        num_points: int = 1000, 
                        x_label: Optional[str] = None, 
                        y_label: Optional[str] = None, 
                        title: Optional[str] = None, 
                        x_scale: str = 'linear', 
                        y_scale: str = 'linear') -> None:
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
        if x_scale == 'log':
            # For log scale, use logarithmically spaced points
            x_min_val, x_max_val = np.min(x), np.max(x)
            if x_min_val <= 0:
                positive_x = x[x > 0]
                if positive_x.size > 0:
                    x_min_val = np.min(positive_x)  # Find smallest positive value
                else: # All values are <=0, log scale is problematic. Fallback or raise error.
                    # Fallback to linear for safety, or handle as error
                    x_fit = np.linspace(x_min_val, x_max_val, num_points).astype(np.float64)
                    print("Warning: Log scale requested for non-positive data. Using linear scale for fit curve.")
                    # Alternatively, could raise ValueError("Cannot use log scale with non-positive data.")
            if x_min_val > 0 and x_max_val > 0 : # Ensure min and max are positive for logspace
                x_fit = np.logspace(np.log10(x_min_val), np.log10(x_max_val), num_points, dtype=np.float64)
            else: # Fallback if still problematic after trying to find positive min
                x_fit = np.linspace(np.min(x), np.max(x), num_points).astype(np.float64)

        else:
            # For linear scale, use linearly spaced points
            x_fit = np.linspace(np.min(x), np.max(x), num_points).astype(np.float64)
        
        # Calculate y values using the model function
        try:
            y_fit = model_func(cast(Sequence[float], result.beta), x_fit)
            y_model = model_func(cast(Sequence[float], result.beta), x)
            
            # Calculate residuals
            residuals = y - y_model
            
            # Plot data with error bars using translated label
            self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt='o', capsize=3, label=self._get_translation('data_label')) # type: ignore[reportUnknownMemberType]
            
            # Plot fit curve using translated label
            self.ax.plot(x_fit, y_fit, '-', label=self._get_translation('fit_label')) # type: ignore[reportUnknownMemberType]
            
            # Plot residuals
            self.ax_res.errorbar(x, residuals, yerr=sigma_y, fmt='o', capsize=3) # type: ignore[reportUnknownMemberType]
            self.ax_res.axhline(y=0, color='r', linestyle='-', alpha=0.3) # type: ignore[reportUnknownMemberType]
            
            # Set scales
            self.ax.set_xscale(x_scale) # type: ignore[reportUnknownMemberType]
            self.ax.set_yscale(y_scale) # type: ignore[reportUnknownMemberType]
            self.ax_res.set_xscale(x_scale) # type: ignore[reportUnknownMemberType]
            
            # Set labels
            if x_label:
                self.ax.set_xlabel(x_label) # type: ignore[reportUnknownMemberType]
                self.ax_res.set_xlabel(x_label) # type: ignore[reportUnknownMemberType]
            if y_label:
                self.ax.set_ylabel(y_label) # type: ignore[reportUnknownMemberType]
            if title:
                self.ax.set_title(title) # type: ignore[reportUnknownMemberType]
            else:
                # Create title from equation if not provided using translated prefix
                eq_title = equation
                for i, p_sym in enumerate(parameters):
                    eq_title = eq_title.replace(str(p_sym), f"{str(p_sym)}={result.beta[i]:.4f}")
                self.ax.set_title(f"{self._get_translation('fit_title_prefix')} {eq_title}") # type: ignore[reportUnknownMemberType]
            
            # Residuals label using translation
            self.ax_res.set_ylabel(self._get_translation('residuals')) # type: ignore[reportUnknownMemberType]
            
            # Add grid to both plots
            self.ax.grid(True, linestyle='--', alpha=0.7) # type: ignore[reportUnknownMemberType]
            self.ax_res.grid(True, linestyle='--', alpha=0.7) # type: ignore[reportUnknownMemberType]
            
            # Add fit statistics to legend
            self.ax.legend(title=f"χ²={chi2:.2f}, R²={r2:.4f}") # type: ignore[reportUnknownMemberType]
            
            # Ensure tight layout
            self.fig.tight_layout() # type: ignore[reportUnknownMemberType]
            self.canvas.draw() # type: ignore[reportUnknownMemberType]
        
        except Exception as e:
            print(f"Error in plot_fit_results: {str(e)}")
            # If fit plotting fails, at least show the data
            self.plot_data_only(x, y, sigma_x, sigma_y, x_label, y_label, title, x_scale, y_scale)
    
    def update_graph_appearance(self, 
                                title: Optional[str] = None, 
                                x_label: Optional[str] = None, 
                                y_label: Optional[str] = None) -> None:
        """Update graph appearance (title, labels, etc.)
        
        Args:
            title: Plot title
            x_label: X-axis label
            y_label: Y-axis label
        """
        if title:
            self.ax.set_title(title) # type: ignore[reportUnknownMemberType]
        if x_label:
            self.ax.set_xlabel(x_label) # type: ignore[reportUnknownMemberType]
            self.ax_res.set_xlabel(x_label) # type: ignore[reportUnknownMemberType]
        if y_label:
            self.ax.set_ylabel(y_label) # type: ignore[reportUnknownMemberType]
        
        self.fig.tight_layout() # type: ignore[reportUnknownMemberType]
        self.canvas.draw() # type: ignore[reportUnknownMemberType]
    
    def refresh_current_plot(self) -> None:
        """Refresh the current plot with updated language labels"""
        # This method can be called after language change to update plot labels
        # without recalculating the data
        
        # Update residuals ylabel if there's existing content
        if self.ax_res.get_children(): # type: ignore[reportUnknownMemberType]
            self.ax_res.set_ylabel(self._get_translation('residuals')) # type: ignore[reportUnknownMemberType]
        
        # Update legend if it exists
        legend: Optional[MplLegend] = self.ax.get_legend() # type: ignore[reportUnknownMemberType]
        if legend:
            # Get current legend handles and labels
            handles: List[Artist] = legend.legend_handles # type: ignore[reportUnknownMemberType] # Corrected attribute
            original_texts = legend.get_texts() # type: ignore[reportUnknownMemberType]
            labels: List[str] = [text.get_text() for text in original_texts] # type: ignore[reportUnknownMemberType]
            
            # Update translated labels
            updated_labels: List[str] = []
            for label_text in labels:
                # Ensure label_text is treated as str for 'in' operations
                current_label_str = label_text # Removed unnecessary cast
                if 'Dados' in current_label_str or 'Data' in current_label_str:
                    updated_labels.append(self._get_translation('data_label'))
                elif 'Ajuste' in current_label_str or 'Fit' in current_label_str:
                    updated_labels.append(self._get_translation('fit_label'))
                elif 'Resíduos' in current_label_str or 'Residuals' in current_label_str: # Though residuals usually not in main legend
                    updated_labels.append(self._get_translation('residuals'))
                else:
                    updated_labels.append(current_label_str)
            
            # Re-create legend with updated labels and same handles
            legend_title_obj = legend.get_title() # type: ignore[reportUnknownMemberType]
            legend_title_text: Optional[str] = None
            if legend_title_obj and legend_title_obj.get_text(): # type: ignore[reportUnknownMemberType]
                legend_title_text = legend_title_obj.get_text() # type: ignore[reportUnknownMemberType]
            self.ax.legend(handles, updated_labels, title=legend_title_text) # type: ignore[reportUnknownMemberType]
        
        # Update all line labels in the plot
        line: Line2D 
        for line in self.ax.get_lines(): # type: ignore[reportUnknownMemberType]
            label_val: str = cast(str, line.get_label()) 
            # Ensure label_val is treated as str for 'startswith' and 'in' operations
            current_label_str = label_val # Removed unnecessary cast
            if current_label_str and not current_label_str.startswith('_'): 
                if 'Dados' in current_label_str or 'Data' in current_label_str:
                    line.set_label(self._get_translation('data_label')) # type: ignore[reportUnknownMemberType]
                elif 'Ajuste' in current_label_str or 'Fit' in current_label_str:
                    line.set_label(self._get_translation('fit_label')) # type: ignore[reportUnknownMemberType]
        
        # Redraw the canvas
        self.fig.tight_layout() # type: ignore[reportUnknownMemberType]
        self.canvas.draw() # type: ignore[reportUnknownMemberType]


