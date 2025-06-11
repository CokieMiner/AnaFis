"""Graph export manager for curve fitting"""
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, List, Tuple, Optional, cast
import numpy as np
from numpy.typing import NDArray
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.legend import Legend as MplLegend

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
    # AjusteCurvaFrame is expected to have attributes like:
    # fig: Figure
    # ax: Axes
    # ax_res: Axes
    # x: NDArray[np.float64]
    # y: NDArray[np.float64]
    # sigma_x: Optional[NDArray[np.float64]]
    # sigma_y: Optional[NDArray[np.float64]]
    # save_graph_option: StringVar 

class GraphExportManager:
    """Handles exporting and saving graphs for curve fitting"""
    parent: 'AjusteCurvaFrame'
    language: str
    
    def __init__(self, parent: 'AjusteCurvaFrame', language: str = 'pt') -> None:
        """Initialize the graph export manager
        
        Args:
            parent: The parent AjusteCurvaFrame instance
            language: Interface language (default: 'pt')
        """
        self.parent = parent
        self.language = language
    
    def save_graph(self) -> None:
        """Save graph to file"""
        try:
            filetypes: List[Tuple[str, str]] = [
                (TRANSLATIONS[self.language].get('png_files', 'PNG files'), '*.png'),
                (TRANSLATIONS[self.language].get('pdf_files', 'PDF files'), '*.pdf'),
                (TRANSLATIONS[self.language].get('svg_files', 'SVG files'), '*.svg'),
                (TRANSLATIONS[self.language].get('all_files', 'All files'), '*.*')
            ]
            
            filepath_optional: Optional[str] = filedialog.asksaveasfilename( # type: ignore[misc]
                title=TRANSLATIONS[self.language].get('save_graph', "Save Graph"),
                filetypes=filetypes,
                defaultextension=".png"
            )
            
            if not filepath_optional:
                return  # User cancelled
            
            filepath: str = filepath_optional
            
            # Assuming self.parent.save_graph_option is a tk.StringVar
            selected_option = self.parent.save_graph_option
            if selected_option is None:
                # Handle case where save_graph_option might not be initialized, though unlikely if UI is built.
                messagebox.showerror( # type: ignore[misc]
                    TRANSLATIONS[self.language].get('error', "Error"),
                    TRANSLATIONS[self.language].get('internal_error_option', "Internal error: Graph option not found.")
                )
                return
            selected: str = str(selected_option.get()) # Corrected assignment


            fig_size_inches: Tuple[float, float] = cast(Tuple[float, float], tuple(self.parent.fig.get_size_inches())) # type: ignore[reportUnknownMemberType]
            fig_to_save: Figure = plt.figure(figsize=fig_size_inches) # type: ignore[reportUnknownMemberType]
            
            parent_ax: Axes = self.parent.ax
            parent_ax_res: Axes = self.parent.ax_res

            # Data from parent, assuming types are set on AjusteCurvaFrame
            x_data: NDArray[np.float64] = self.parent.x
            y_data: NDArray[np.float64] = self.parent.y
            sigma_x_data: Optional[NDArray[np.float64]] = self.parent.sigma_x
            sigma_y_data: Optional[NDArray[np.float64]] = self.parent.sigma_y

            if selected == "full":
                self.parent.fig.savefig(filepath, dpi=300, bbox_inches='tight') # type: ignore[reportUnknownMemberType]
            elif selected == "fit_and_data":
                ax: Axes = fig_to_save.add_subplot(111) # type: ignore[reportUnknownMemberType]
                for line in parent_ax.lines: # Removed # type: Line2D
                    ax.plot(line.get_xdata(), line.get_ydata(),  # type: ignore[reportUnknownMemberType]
                            color=line.get_color(), linestyle=line.get_linestyle(), 
                            marker=line.get_marker(), label=line.get_label())
                for container in parent_ax.containers: # Removed # type: Container
                    if hasattr(container, 'has_xerr') or hasattr(container, 'has_yerr'):
                        ax.errorbar(x_data, y_data, xerr=sigma_x_data, yerr=sigma_y_data, fmt='none') # type: ignore[reportUnknownMemberType]
                        break
                ax.set_title(parent_ax.get_title()) # type: ignore[reportUnknownMemberType]
                ax.set_xlabel(parent_ax.get_xlabel()) # type: ignore[reportUnknownMemberType]
                ax.set_ylabel(parent_ax.get_ylabel()) # type: ignore[reportUnknownMemberType]
                ax.set_xscale(parent_ax.get_xscale()) # type: ignore[reportUnknownMemberType]
                ax.set_yscale(parent_ax.get_yscale()) # type: ignore[reportUnknownMemberType]
                parent_legend: Optional[MplLegend] = parent_ax.legend_
                if parent_legend:
                    ax.legend() # type: ignore[reportUnknownMemberType]
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight') # type: ignore[reportUnknownMemberType]
                plt.close(fig_to_save)
            elif selected == "only_data":
                ax: Axes = fig_to_save.add_subplot(111) # type: ignore[reportUnknownMemberType]
                ax.errorbar(x_data, y_data, xerr=sigma_x_data, yerr=sigma_y_data, fmt='o', label=TRANSLATIONS[self.language].get('data_label', 'Data')) # type: ignore[reportUnknownMemberType]
                ax.set_title(parent_ax.get_title()) # type: ignore[reportUnknownMemberType]
                ax.set_xlabel(parent_ax.get_xlabel()) # type: ignore[reportUnknownMemberType]
                ax.set_ylabel(parent_ax.get_ylabel()) # type: ignore[reportUnknownMemberType]
                ax.set_xscale(parent_ax.get_xscale()) # type: ignore[reportUnknownMemberType]
                ax.set_yscale(parent_ax.get_yscale()) # type: ignore[reportUnknownMemberType]
                ax.legend() # type: ignore[reportUnknownMemberType]
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight') # type: ignore[reportUnknownMemberType]
                plt.close(fig_to_save)
            elif selected == "only_fit":
                ax: Axes = fig_to_save.add_subplot(111) # type: ignore[reportUnknownMemberType]
                for line in parent_ax.lines: # Removed # type: Line2D
                    # Added type ignore for the comparison if Pylance flags it
                    if line.get_marker() == '' or line.get_marker() is None: # type: ignore[reportUnnecessaryComparison]
                        ax.plot(line.get_xdata(), line.get_ydata(),  # type: ignore[reportUnknownMemberType]
                                color=line.get_color(), linestyle=line.get_linestyle(),
                                label=TRANSLATIONS[self.language].get('fit_label', 'Fit'))
                ax.set_title(parent_ax.get_title()) # type: ignore[reportUnknownMemberType]
                ax.set_xlabel(parent_ax.get_xlabel()) # type: ignore[reportUnknownMemberType]
                ax.set_ylabel(parent_ax.get_ylabel()) # type: ignore[reportUnknownMemberType]
                ax.set_xscale(parent_ax.get_xscale()) # type: ignore[reportUnknownMemberType]
                ax.set_yscale(parent_ax.get_yscale()) # type: ignore[reportUnknownMemberType]
                ax.legend() # type: ignore[reportUnknownMemberType]
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight') # type: ignore[reportUnknownMemberType]
                plt.close(fig_to_save)
            elif selected == "only_residuals":
                ax: Axes = fig_to_save.add_subplot(111) # type: ignore[reportUnknownMemberType]
                for line in parent_ax_res.lines: # Removed # type: Line2D
                    ax.plot(line.get_xdata(), line.get_ydata(),  # type: ignore[reportUnknownMemberType]
                            color=line.get_color(), linestyle=line.get_linestyle(), 
                            marker=line.get_marker())
                ax.set_title(TRANSLATIONS[self.language].get('residuals_title', "Residuals")) # type: ignore[reportUnknownMemberType]
                ax.set_xlabel(parent_ax_res.get_xlabel()) # type: ignore[reportUnknownMemberType]
                ax.set_ylabel(parent_ax_res.get_ylabel()) # type: ignore[reportUnknownMemberType]
                ax.set_xscale(parent_ax_res.get_xscale()) # type: ignore[reportUnknownMemberType]
                ax.grid(True, linestyle='--', alpha=0.7) # type: ignore[reportUnknownMemberType]
                fig_to_save.tight_layout()
                fig_to_save.savefig(filepath, dpi=300, bbox_inches='tight') # type: ignore[reportUnknownMemberType]
                plt.close(fig_to_save)
            else:
                self.parent.fig.savefig(filepath, dpi=300, bbox_inches='tight') # type: ignore[reportUnknownMemberType]

        except Exception as e:
            print(f"Error in save_graph: {str(e)}")
            messagebox.showerror( # type: ignore[misc]
                TRANSLATIONS[self.language].get('error', "Error"), 
                f"{TRANSLATIONS[self.language].get('save_error', 'Error saving graph')}: {str(e)}"
            )