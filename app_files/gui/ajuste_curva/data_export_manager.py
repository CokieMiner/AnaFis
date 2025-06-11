"""Data export manager for curve fitting"""
import json
import pandas as pd
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Any, Dict # Added TYPE_CHECKING, Any, and Dict

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame # Import for type hinting

class DataExportManager:
    """Handles exporting data and fit results to various file formats"""
    
    def __init__(self, parent: 'AjusteCurvaFrame', language: str = 'pt') -> None: # Added type hints
        """Initialize the data export manager
        
        Args:
            parent: The parent AjusteCurvaFrame instance
            language: Interface language (default: 'pt')
        """
        self.parent = parent
        self.language = language
    
    def export_results(self) -> None: # Added return type hint
        """Export fit results to file"""
        if not hasattr(self.parent, 'last_result') or self.parent.last_result is None:
            messagebox.showwarning(TRANSLATIONS[self.language].get('warning', "Aviso"), TRANSLATIONS[self.language].get('no_fit_to_export', "Nenhum ajuste para exportar.")) # type: ignore[misc]
            return
            
        filename: str = filedialog.asksaveasfilename( # Added type hint
            title=TRANSLATIONS[self.language].get('export_results_title', "Exportar Resultados"),
            filetypes=[
                (TRANSLATIONS[self.language].get('csv_files', "CSV"), "*.csv"), 
                (TRANSLATIONS[self.language].get('json_files', "JSON"), "*.json"), 
                (TRANSLATIONS[self.language].get('text_files', "Texto"), "*.txt")
            ]
        )
        if not filename:
            return
            
        try:
            if filename.endswith('.json'):
                self.export_json(filename)
            elif filename.endswith('.csv'):
                self.export_csv(filename)
            else:
                # Ensure .txt extension if no other recognized extension is present
                if not any(filename.endswith(ext) for ext in ['.csv', '.json', '.txt']):
                    filename += '.txt'
                self.export_txt(filename)
            messagebox.showinfo(TRANSLATIONS[self.language].get('success', "Sucesso"), TRANSLATIONS[self.language].get('results_exported', f"Resultados exportados para {filename}")) # type: ignore[misc]
        except Exception as e:
            messagebox.showerror(TRANSLATIONS[self.language].get('error', "Erro"), TRANSLATIONS[self.language].get('export_error', f"Erro ao exportar: {str(e)}")) # type: ignore[misc]
    
    def export_json(self, filename: str) -> None: # Added type hints
        """Export fit results to JSON format"""
        data: Dict[str, Any] = { # Added type hint for data
            "equation": self.parent.equacao,
            "parameters": [str(p) for p in self.parent.parametros],
            "values": self.parent.last_result.beta.tolist(), # type: ignore[reportUnknownMemberType]
            "errors": self.parent.last_result.sd_beta.tolist(), # type: ignore[reportUnknownMemberType]
            "chi_squared": float(self.parent.last_chi2),
            "r_squared": float(self.parent.last_r2),
            "data": {
                "x": self.parent.x.tolist(),
                "y": self.parent.y.tolist(),
                "sigma_x": self.parent.sigma_x.tolist(),
                "sigma_y": self.parent.sigma_y.tolist()
            }
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def export_csv(self, filename: str) -> None: # Added type hints
        """Export fit results to CSV format"""
        # Create a DataFrame with parameter values and errors
        param_names = [str(p) for p in self.parent.parametros]
        param_values = self.parent.last_result.beta # type: ignore[reportUnknownMemberType]
        param_errors = self.parent.last_result.sd_beta # type: ignore[reportUnknownMemberType]
        
        # Create a DataFrame for parameters
        df_params = pd.DataFrame({
            "parameter": param_names,
            "value": param_values,
            "error": param_errors
        })
        
        # Create a DataFrame for statistics
        df_stats = pd.DataFrame({
            "statistic": ["chi_squared", "r_squared"],
            "value": [self.parent.last_chi2, self.parent.last_r2]
        })
        
        # Create a DataFrame for original data
        df_data = pd.DataFrame({
            "x": self.parent.x,
            "sigma_x": self.parent.sigma_x,
            "y": self.parent.y,
            "sigma_y": self.parent.sigma_y
        })
        
        # Write to CSV, adding empty rows between sections
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Parameters\n")
            df_params.to_csv(f, index=False)
            f.write("\n# Statistics\n")
            df_stats.to_csv(f, index=False)
            f.write("\n# Data\n")
            df_data.to_csv(f, index=False)
    
    def export_txt(self, filename: str) -> None: # Added type hints
        """Export fit results to plain text format"""
        with open(filename, 'w', encoding='utf-8') as f:
            if self.parent.results_text: # Check if results_text exists
                f.write(self.parent.results_text.get(1.0, "end-1c"))
            f.write("\n\nEquação: " + self.parent.equacao + "\n")
            f.write("\nDados originais:\n")
            f.write("x\tsigma_x\ty\tsigma_y\n")
            for i in range(len(self.parent.x)):
                f.write(f"{self.parent.x[i]}\t{self.parent.sigma_x[i]}\t{self.parent.y[i]}\t{self.parent.sigma_y[i]}\n")
    
    def switch_language(self, language: str) -> None: # Added type hints
        """Update language for this component"""
        self.language = language