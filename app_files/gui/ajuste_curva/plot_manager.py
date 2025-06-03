"""Plotting functions for curve fitting GUI"""
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Callable, Optional, Union, cast
from matplotlib.axes import Axes
from matplotlib.figure import Figure

class PlotManager:
    """Manages plotting for curve fitting GUI"""
    
    def __init__(self, figure, canvas, language: str = 'pt'):
        """Initialize plot manager
        
        Args:
            figure: Matplotlib figure object
            canvas: Matplotlib canvas widget
            language (str, optional): UI language. Defaults to 'pt'.
        """
        self.fig = figure
        self.canvas = canvas
        self.language = language
        
        # Translations
        self.translations = {
            'pt': {
                'data_points': 'Pontos de dados',
                'fit_curve': 'Curva de ajuste',
                'equation': 'Equação',
                'chi_squared': 'χ',
                'reduced_chi_squared': 'χ reduzido',
                'r_squared': 'R'
            },
            'en': {
                'data_points': 'Data points',
                'fit_curve': 'Fit curve',
                'equation': 'Equation',
                'chi_squared': 'χ',
                'reduced_chi_squared': 'Reduced χ',
                'r_squared': 'R'
            }
        }
        
        # Create axes immediately to avoid None errors
        self._create_axes()
    
    def _create_axes(self):
        """Create the matplotlib axes"""
        plt.style.use('default')
        self.fig.clear()
        
        # Create subplots and ensure they're properly assigned
        axes = self.fig.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
        
        # Handle both array and single axes case
        if isinstance(axes, np.ndarray):
            self.ax = cast(Axes, axes[0])
            self.ax_res = cast(Axes, axes[1])
        else:
            self.ax = cast(Axes, axes)
            # Create second axis manually if needed
            self.ax_res = cast(Axes, self.fig.add_subplot(212))
    
    def initialize_empty_plot(self):
        """Initialize empty plot with proper axes setup"""
        # Clear both axes
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
    
    def plot_data_only(self, x, y, sigma_x, sigma_y, x_label=None, y_label=None, title=None, x_scale='linear', y_scale='linear'):
        """Plot only the data points without fit curve"""
        if len(x) == 0 or len(y) == 0:
            return
            
        self.ax.clear()
        self.ax_res.clear()
        
        # Plot data points
        self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, 
                      fmt='o', label=self.translations[self.language]['data_points'])
        
        # Setup axes
        if title:
            self.ax.set_title(title)
        self.ax.set_xlabel(x_label if x_label else "X")
        self.ax.set_ylabel(y_label if y_label else "Y")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # Setup residuals plot (empty for now)
        self.ax_res.set_xlabel(x_label if x_label else "X")
        self.ax_res.set_ylabel('Resíduos')
        self.ax_res.grid(True, alpha=0.3)
        self.ax_res.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        
        # Apply scales
        self.ax.set_xscale(x_scale)
        self.ax.set_yscale(y_scale)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def plot_fit_results(self, x, y, sigma_x, sigma_y, 
                        model_func, result, chi2, r2, equation, 
                        parameters, num_points, 
                        x_label=None, y_label=None, title=None,
                        x_scale='linear', y_scale='linear'):
        """Plot fitting results"""
        # Calculate fitted curve and residuals
        y_pred = model_func(result.beta, x)
        residuals = y - y_pred
        
        # Clear plots
        self.ax.clear()
        self.ax_res.clear()
        
        # Plot data points with error bars
        self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt='o', 
                      label=self.translations[self.language]['data_points'])
        
        # Plot fitted curve
        x_fit = np.linspace(min(x), max(x), num_points)
        self.ax.plot(x_fit, model_func(result.beta, x_fit), 'r-', 
                  label=self.translations[self.language]['fit_curve'])
        
        # Plot residuals
        self.ax_res.scatter(x, residuals, color='green', marker='x', label='Resíduos')
        self.ax_res.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        
        # Set labels
        if title:
            self.ax.set_title(title)
        self.ax.set_xlabel(x_label if x_label else "X")
        self.ax.set_ylabel(y_label if y_label else "Y")
        self.ax_res.set_xlabel(x_label if x_label else "X")
        self.ax_res.set_ylabel('Resíduos')
        
        # Set scales
        self.ax.set_xscale(x_scale)
        self.ax.set_yscale(y_scale)
        
        # Add legend and grid
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        self.ax_res.grid(True, alpha=0.3)
        
        # Add text box with fit information
        texto_info = f"{self.translations[self.language]['equation']}: y = {equation}\n"
        texto_info += '\n'.join([f"{p} = {v:.6f}  {e:.6f}" for p, v, e in zip(parameters, result.beta, result.sd_beta)])
        texto_info += f"\n{self.translations[self.language]['chi_squared']}: {chi2:.2f}"
        texto_info += f"\n{self.translations[self.language]['reduced_chi_squared']}: {result.res_var:.2f}"
        texto_info += f"\n{self.translations[self.language]['r_squared']}: {r2:.4f}"
        
        self.ax.text(
            0.98, 0.02,
            texto_info,
            transform=self.ax.transAxes,
            fontsize=7,
            bbox=dict(facecolor='white', alpha=0.5),
            ha='right',
            va='bottom'
        )
        
        # Update display
        self.fig.tight_layout()
        self.canvas.draw()
    
    def save_graph(self, filename):
        """Save the graph to a file"""
        self.canvas.figure.savefig(filename)
