"""Graph export manager for curve fitting"""
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox

from app_files.utils.constants import TRANSLATIONS

class GraphExportManager:
    """Handles exporting and saving graphs for curve fitting"""
    
    def __init__(self, parent, language='pt'):
        """Initialize the graph export manager
        
        Args:
            parent: The parent AjusteCurvaFrame instance
            language: Interface language (default: 'pt')
        """
        self.parent = parent
        self.language = language
    
    def save_graph(self):
        """Save graph to file"""
        try:
            # Get file path from user
            filetypes = [
                ('PNG files', '*.png'),
                ('PDF files', '*.pdf'),
                ('SVG files', '*.svg'),
                ('All files', '*.*')
            ]
            
            filepath = filedialog.asksaveasfilename(
                title=TRANSLATIONS[self.language].get('save_graph', "Save Graph"),
                filetypes=filetypes,
                defaultextension=".png"
            )
            
            if not filepath:
                return  # User cancelled
                
            # Get the selected graph type from save_graph_option
            selected = self.parent.save_graph_option.get()

            # Handle different plot types for saving
            fig_to_save = plt.figure(figsize=self.parent.fig.get_size_inches())
            
            if selected == "full":
                # Save the entire figure as is
                self.parent.fig.savefig(filepath, dpi=300, bbox_inches='tight')
            elif selected == "fit_and_data":
                # Create a new figure with just main plot (no residuals)
                ax = fig_to_save.add_subplot(111)
                # Copy data and fit lines from main axis
                for line in self.parent.ax.lines:
                    ax.plot(line.get_xdata(), line.get_ydata(), 
                            color=line.get_color(), linestyle=line.get_linestyle(), 
                            marker=line.get_marker(), label=line.get_label())
                # Copy error bars if they exist
                for container in self.parent.ax.containers:
                    if hasattr(container, 'has_xerr') or hasattr(container, 'has_yerr'):
                        ax.errorbar(self.parent.x, self.parent.y, xerr=self.parent.sigma_x, yerr=self.parent.sigma_y, fmt='none')
                        break
                ax.set_title(self.parent.ax.get_title())
                ax.set_xlabel(self.parent.ax.get_xlabel())
                ax.set_ylabel(self.parent.ax.get_ylabel())
                ax.set_xscale(self.parent.ax.get_xscale())
                ax.set_yscale(self.parent.ax.get_yscale())
                if self.parent.ax.legend_:
                    ax.legend()
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close(fig_to_save)
            elif selected == "only_data":
                # Create a new figure with just data points
                ax = fig_to_save.add_subplot(111)
                # Plot only data points from main axis
                ax.errorbar(self.parent.x, self.parent.y, xerr=self.parent.sigma_x, yerr=self.parent.sigma_y, fmt='o', label='Dados')
                ax.set_title(self.parent.ax.get_title())
                ax.set_xlabel(self.parent.ax.get_xlabel())
                ax.set_ylabel(self.parent.ax.get_ylabel())
                ax.set_xscale(self.parent.ax.get_xscale())
                ax.set_yscale(self.parent.ax.get_yscale())
                ax.legend()
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close(fig_to_save)
            elif selected == "only_fit":
                # Create a new figure with just fit curve
                ax = fig_to_save.add_subplot(111)
                # Find and plot just the fit line
                for line in self.parent.ax.lines:
                    if line.get_marker() == '' or line.get_marker() is None:  # Likely the fit curve
                        ax.plot(line.get_xdata(), line.get_ydata(), 
                                color=line.get_color(), linestyle=line.get_linestyle(),
                                label='Ajuste')
                ax.set_title(self.parent.ax.get_title())
                ax.set_xlabel(self.parent.ax.get_xlabel())
                ax.set_ylabel(self.parent.ax.get_ylabel())
                ax.set_xscale(self.parent.ax.get_xscale())
                ax.set_yscale(self.parent.ax.get_yscale())
                ax.legend()
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close(fig_to_save)
            elif selected == "only_residuals":
                # Create a new figure with just residuals
                ax = fig_to_save.add_subplot(111)
                # Copy residuals plot
                for line in self.parent.ax_res.lines:
                    ax.plot(line.get_xdata(), line.get_ydata(), 
                            color=line.get_color(), linestyle=line.get_linestyle(), 
                            marker=line.get_marker())
                ax.set_title("Resíduos")
                ax.set_xlabel(self.parent.ax_res.get_xlabel())
                ax.set_ylabel(self.parent.ax_res.get_ylabel())
                ax.set_xscale(self.parent.ax_res.get_xscale())
                ax.grid(True, linestyle='--', alpha=0.7)
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close(fig_to_save)
            else:
                # Default fallback - save the entire figure
                self.parent.fig.savefig(filepath, dpi=300, bbox_inches='tight')

        except Exception as e:
            print(f"Error in save_graph: {str(e)}")
            messagebox.showerror(
                TRANSLATIONS[self.language].get('error', "Error"), 
                f"{TRANSLATIONS[self.language].get('save_error', 'Error saving graph')}: {str(e)}"
            )