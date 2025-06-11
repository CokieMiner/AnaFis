"""Data handling module for curve fitting GUI"""
import os
import json
import numpy as np
import pandas as pd
from tkinter import messagebox
from typing import Tuple, List, Any, Dict, cast # Added cast back
from numpy.typing import NDArray

def read_file(file_name: str, language: str = 'pt') -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], pd.DataFrame]:
    """Read data from file
    
    Args:
        file_name (str): Path to the data file
        language (str, optional): UI language. Defaults to 'pt'.
        
    Returns:
        Tuple containing x, sigma_x, y, sigma_y arrays and a DataFrame for preview
    """
    error_messages = {
        'file_not_found': {
            'pt': "O arquivo '{file}' não foi encontrado.",
            'en': "The file '{file}' was not found."
        },
        'processing_error': {
            'pt': "Erro ao processar o arquivo: {error}",
            'en': "Error processing the file: {error}"
        }
    }

    if not os.path.isfile(file_name):
        messagebox.showerror( # type: ignore[misc]
            "Erro" if language == 'pt' else "Error",
            error_messages['file_not_found'][language].format(file=file_name)
        )
        raise FileNotFoundError(error_messages['file_not_found'][language].format(file=file_name))

    try:
        # Check file extension and read accordingly
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()
        
        if ext in ['.xlsx', '.xls']:
            # Excel file support
            df: pd.DataFrame = pd.read_excel(file_name) # type: ignore[reportUnknownMemberType]
            if len(df.columns) < 4:
                raise ValueError("Excel deve ter pelo menos 4 colunas: x, sigma_x, y, sigma_y")
            x = cast(NDArray[np.float64], df.iloc[:, 0].to_numpy(dtype=float)) # type: ignore[reportUnknownMemberType]
            sigma_x = cast(NDArray[np.float64], df.iloc[:, 1].to_numpy(dtype=float)) # type: ignore[reportUnknownMemberType]
            y = cast(NDArray[np.float64], df.iloc[:, 2].to_numpy(dtype=float)) # type: ignore[reportUnknownMemberType]
            sigma_y = cast(NDArray[np.float64], df.iloc[:, 3].to_numpy(dtype=float)) # type: ignore[reportUnknownMemberType]
            return x, sigma_x, y, sigma_y, df
            
        elif ext == '.json':
            # JSON file support
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            x = np.array(data['x'], dtype=np.float64)
            sigma_x = np.array(data['sigma_x'], dtype=np.float64)
            y = np.array(data['y'], dtype=np.float64)
            sigma_y = np.array(data['sigma_y'], dtype=np.float64)
            preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})
            return x, sigma_x, y, sigma_y, preview_data
        
        else:
            # Text/CSV file processing (original logic)
            if ext.lower() == ".csv":
                delimiter = ','
            else:
                delimiter = '\t'

            with open(file_name, 'r', encoding='utf-8') as f:
                _ = f.readline() # Skip header
                lines = f.readlines()
                
            if len(lines) == 0:
                messagebox.showerror("Erro ao ler arquivo", "O arquivo está vazio ou só contém o cabeçalho.") # type: ignore[misc]
                raise ValueError("O arquivo está vazio ou só contém o cabeçalho.")

            # Check number of columns
            for i, line in enumerate(lines):
                parts = line.strip().split(delimiter)
                if len(parts) != 4:
                    messagebox.showerror("Erro ao ler arquivo", # type: ignore[misc]
                        f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")
                    raise ValueError(f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")
            
            # Load data using numpy
            # Use 'lines' directly with genfromtxt if skip_header is handled by readline, or adjust skip_header
            # For simplicity, re-opening or using a different approach for genfromtxt might be cleaner if header is complex
            # Sticking to original logic for now, assuming genfromtxt handles the file path correctly after readline
            dados: NDArray[np.str_] = np.genfromtxt(file_name, delimiter=delimiter, skip_header=1, dtype=str, encoding='utf-8') # type: ignore
            dados = np.char.replace(dados, ',', '.')
            x: NDArray[np.float64] = dados[:, 0].astype(np.float64)
            sigma_x: NDArray[np.float64] = dados[:, 1].astype(np.float64)
            y: NDArray[np.float64] = dados[:, 2].astype(np.float64)
            sigma_y: NDArray[np.float64] = dados[:, 3].astype(np.float64)
            
            # Create preview dataframe
            preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})
            return x, sigma_x, y, sigma_y, preview_data
            
    except Exception as e:
        messagebox.showerror( # type: ignore[misc]
            "Erro" if language == 'pt' else "Error",
            error_messages['processing_error'][language].format(error=str(e))
        )
        raise

def export_json(filename: str, equation: str, parameters: List[str], result: Any, chi2: float, r2: float) -> None:
    """Export results to JSON format"""
    beta_values = result.beta  # type: ignore[attr-defined]
    sd_beta_values = result.sd_beta  # type: ignore[attr-defined]
    res_variance = result.res_var  # type: ignore[attr-defined]

    # Ensure beta_values and sd_beta_values are lists for JSON serialization
    try:
        beta_list = beta_values.tolist()
    except AttributeError: # If they are already lists or other iterables
        beta_list = list(beta_values)
    
    try:
        sd_beta_list = sd_beta_values.tolist()
    except AttributeError:
        sd_beta_list = list(sd_beta_values)

    data: Dict[str, Any] = {
        'equation': equation,
        'parameters': parameters,
        'values': beta_list,
        'errors': sd_beta_list,
        'chi_squared': chi2,
        'r_squared': r2,
        'residual_variance': res_variance
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
def export_txt(filename: str, results_text: str) -> None:
    """Export results to text format"""
    with open(filename, 'w', encoding='utf-8') as f: # Added encoding for consistency
        f.write(results_text)
