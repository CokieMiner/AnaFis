"""Data handling module for curve fitting GUI"""
import os
import json
import numpy as np
import pandas as pd
from tkinter import messagebox
from typing import Tuple, List, Any

def read_file(file_name: str, language: str = 'pt') -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
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
        messagebox.showerror(
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
            df = pd.read_excel(file_name)
            if len(df.columns) < 4:
                raise ValueError("Excel deve ter pelo menos 4 colunas: x, sigma_x, y, sigma_y")
            x = df.iloc[:, 0].values.astype(float)
            sigma_x = df.iloc[:, 1].values.astype(float)
            y = df.iloc[:, 2].values.astype(float) 
            sigma_y = df.iloc[:, 3].values.astype(float)
            return x, sigma_x, y, sigma_y, df
            
        elif ext == '.json':
            # JSON file support
            with open(file_name, 'r') as f:
                data = json.load(f)
            x = np.array(data['x'], dtype=float)
            sigma_x = np.array(data['sigma_x'], dtype=float)
            y = np.array(data['y'], dtype=float)
            sigma_y = np.array(data['sigma_y'], dtype=float)
            preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})
            return x, sigma_x, y, sigma_y, preview_data
        
        else:
            # Text/CSV file processing (original logic)
            if ext.lower() == ".csv":
                delimiter = ','
            else:
                delimiter = '\t'

            with open(file_name, 'r') as f:
                header = f.readline()
                lines = f.readlines()
                
            if len(lines) == 0:
                messagebox.showerror("Erro ao ler arquivo", "O arquivo está vazio ou só contém o cabeçalho.")
                raise ValueError("O arquivo está vazio ou só contém o cabeçalho.")

            # Check number of columns
            for i, line in enumerate(lines):
                parts = line.strip().split(delimiter)
                if len(parts) != 4:
                    messagebox.showerror("Erro ao ler arquivo",
                        f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")
                    raise ValueError(f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2}).")
            
            # Load data using numpy
            dados = np.genfromtxt(file_name, delimiter=delimiter, skip_header=1, dtype=str)
            dados = np.char.replace(dados, ',', '.')
            x = dados[:, 0].astype(float)
            sigma_x = dados[:, 1].astype(float)
            y = dados[:, 2].astype(float)
            sigma_y = dados[:, 3].astype(float)
            
            # Create preview dataframe
            preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})
            return x, sigma_x, y, sigma_y, preview_data
            
    except Exception as e:
        messagebox.showerror(
            "Erro" if language == 'pt' else "Error",
            error_messages['processing_error'][language].format(error=str(e))
        )
        raise

def export_json(filename: str, equation: str, parameters: List, result: Any, chi2: float, r2: float) -> None:
    """Export results to JSON format"""
    data = {
        'equation': equation,
        'parameters': {str(p): {'value': float(v), 'error': float(e)} 
                      for p, v, e in zip(parameters, result.beta, result.sd_beta)},
        'statistics': {
            'chi_squared': float(chi2),
            'reduced_chi_squared': float(result.res_var),
            'r_squared': float(r2)
        }
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
        
def export_csv(filename: str, parameters: List, result: Any) -> None:
    """Export results to CSV format"""
    df = pd.DataFrame({
        'Parameter': [str(p) for p in parameters],
        'Value': result.beta,
        'Error': result.sd_beta
    })
    df.to_csv(filename, index=False)
    
def export_txt(filename: str, results_text: str) -> None:
    """Export results to text format"""
    with open(filename, 'w') as f:
        f.write(results_text)
