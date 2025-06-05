"""Plot manager for curve fitting"""
import numpy as np

from app_files.utils.constants import TRANSLATIONS

class PlotManager:
    """Handles plotting data and fit results for curve fitting"""
    
    def __init__(self, fig, ax, ax_res, canvas, language='pt'):
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
        
    def set_language(self, language):
        """Set the language for plot labels
        
        Args:
            language: Language code ('pt' or 'en')
        """
        self.language = language
        
    def _get_translation(self, key):
        """Get translation for a given key
        
        Args:
            key: Translation key
            
        Returns:
            Translated string
        """
        return TRANSLATIONS.get(self.language, {}).get(key, key)
        
    def initialize_empty_plot(self):
        """Initialize an empty plot"""
        self.ax.clear()
        self.ax_res.clear()
        
        # Add grid to main plot and residuals
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax_res.grid(True, linestyle='--', alpha=0.7)
        
        # Default labels using translations
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax_res.set_xlabel('X')
        self.ax_res.set_ylabel(self._get_translation('residuals'))
        
        # Ensure tight layout
        self.fig.tight_layout()
        self.canvas.draw()
    
    def plot_data_only(self, x, y, sigma_x, sigma_y, x_label=None, y_label=None, title=None, x_scale='linear', y_scale='linear'):
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
        self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt='o', capsize=3, label=self._get_translation('data_label'))
        
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
        self.ax_res.set_ylabel(self._get_translation('residuals'))
        
        # Add grid to both plots
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax_res.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        self.ax.legend()
        
        # Ensure tight layout
        self.fig.tight_layout()
        self.canvas.draw()
    
    def plot_fit_results(self, x, y, sigma_x, sigma_y, model_func, result, chi2, r2, equation, parameters, num_points=1000, 
                        x_label=None, y_label=None, title=None, x_scale='linear', y_scale='linear'):
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
        if x_scale == 'log':
            # For log scale, use logarithmically spaced points
            x_min, x_max = np.min(x), np.max(x)
            if x_min <= 0:
                x_min = np.min(x[x > 0])  # Find smallest positive value
            x_fit = np.logspace(np.log10(x_min), np.log10(x_max), num_points)
        else:
            # For linear scale, use linearly spaced points
            x_fit = np.linspace(np.min(x), np.max(x), num_points)
        
        # Calculate y values using the model function
        try:
            y_fit = model_func(result.beta, x_fit)
            y_model = model_func(result.beta, x)
            
            # Calculate residuals
            residuals = y - y_model
            
            # Plot data with error bars using translated label
            self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt='o', capsize=3, label=self._get_translation('data_label'))
            
            # Plot fit curve using translated label
            self.ax.plot(x_fit, y_fit, '-', label=self._get_translation('fit_label'))
            
            # Plot residuals
            self.ax_res.errorbar(x, residuals, yerr=sigma_y, fmt='o', capsize=3)
            self.ax_res.axhline(y=0, color='r', linestyle='-', alpha=0.3)
            
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
            else:
                # Create title from equation if not provided using translated prefix
                eq_title = equation
                for i, p in enumerate(parameters):
                    eq_title = eq_title.replace(str(p), f"{str(p)}={result.beta[i]:.4f}")
                self.ax.set_title(f"{self._get_translation('fit_title_prefix')} {eq_title}")
            
            # Residuals label using translation
            self.ax_res.set_ylabel(self._get_translation('residuals'))
            
            # Add grid to both plots
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax_res.grid(True, linestyle='--', alpha=0.7)
            
            # Add fit statistics to legend
            self.ax.legend(title=f"χ²={chi2:.2f}, R²={r2:.4f}")
            
            # Ensure tight layout
            self.fig.tight_layout()
            self.canvas.draw()
        
        except Exception as e:
            print(f"Error in plot_fit_results: {str(e)}")
            # If fit plotting fails, at least show the data
            self.plot_data_only(x, y, sigma_x, sigma_y, x_label, y_label, title, x_scale, y_scale)
    
    def update_graph_appearance(self, title=None, x_label=None, y_label=None):
        """Update graph appearance (title, labels, etc.)
        
        Args:
            title: Plot title
            x_label: X-axis label
            y_label: Y-axis label
        """
        if title:
            self.ax.set_title(title)
        if x_label:
            self.ax.set_xlabel(x_label)
            self.ax_res.set_xlabel(x_label)
        if y_label:
            self.ax.set_ylabel(y_label)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def refresh_current_plot(self):
        """Refresh the current plot with updated language labels"""
        # This method can be called after language change to update plot labels
        # without recalculating the data
        
        # Update residuals ylabel if there's existing content
        if self.ax_res.get_children():
            self.ax_res.set_ylabel(self._get_translation('residuals'))
        
        # Update legend if it exists
        legend = self.ax.get_legend()
        if legend:
            # Get current legend handles and labels
            handles = legend.legendHandles
            labels = [text.get_text() for text in legend.get_texts()]
            
            # Update translated labels
            updated_labels = []
            for label in labels:
                if 'Dados' in label or 'Data' in label:
                    updated_labels.append(self._get_translation('data_label'))
                elif 'Ajuste' in label or 'Fit' in label:
                    updated_labels.append(self._get_translation('fit_label'))
                elif 'Resíduos' in label or 'Residuals' in label:
                    updated_labels.append(self._get_translation('residuals'))
                else:
                    updated_labels.append(label)
            
            # Re-create legend with updated labels and same handles
            legend_title = legend.get_title().get_text() if legend.get_title() else None
            self.ax.legend(handles, updated_labels, title=legend_title)
        
        # Update all line labels in the plot
        for line in self.ax.get_lines():
            label = line.get_label()
            if label and not label.startswith('_'):  # Skip auto-generated labels
                if 'Dados' in label or 'Data' in label:
                    line.set_label(self._get_translation('data_label'))
                elif 'Ajuste' in label or 'Fit' in label:
                    line.set_label(self._get_translation('fit_label'))
        
        # Redraw the canvas
        self.fig.tight_layout()
        self.canvas.draw()


