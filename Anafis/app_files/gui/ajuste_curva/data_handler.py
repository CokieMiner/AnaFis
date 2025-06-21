"""Data handling module for curve fitting GUI"""
import os
import json
import numpy as np
import pandas as pd
from tkinter import messagebox
from typing import Tuple, cast
from numpy.typing import NDArray
from app_files.utils.constants import TRANSLATIONS

def read_file(file_name: str, language: str = 'pt') -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], pd.DataFrame]:
    """Read data from file
    
    Args:
        file_name (str): Path to the data file
        language (str, optional): UI language. Defaults to 'pt'.
    
    Returns:
        Tuple containing x, sigma_x, y, sigma_y arrays and a DataFrame for preview
    """
    
    if not os.path.isfile(file_name):
        messagebox.showerror( # type: ignore[misc]
            TRANSLATIONS[language]['error'],
            TRANSLATIONS[language]['file_not_found'].format(file=file_name)
        )
        raise FileNotFoundError(TRANSLATIONS[language]['file_not_found'].format(file=file_name))

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
                messagebox.showerror(TRANSLATIONS[language]['file_read_error'], TRANSLATIONS[language]['file_empty_error'])  # type: ignore[misc]
                raise ValueError(TRANSLATIONS[language]['file_empty_error'])
                  # Check number of columns - support 2, 3, and 4 column formats
            num_columns = None
            for i, line in enumerate(lines):
                parts = line.strip().split(delimiter)
                if num_columns is None:
                    num_columns = len(parts)
                    if num_columns == 1:
                        # Single column - provide helpful guidance
                        messagebox.showerror(TRANSLATIONS[language]['file_read_error'],  # type: ignore[misc]
                            f"{TRANSLATIONS[language]['file_single_column_error']}\n\n" +
                            f"{TRANSLATIONS[language]['file_format_guidance']}")
                        raise ValueError(TRANSLATIONS[language]['file_single_column_error'])
                    elif num_columns >= 5:
                        # Too many columns - provide fallback suggestion
                        messagebox.showerror(TRANSLATIONS[language]['file_read_error'],  # type: ignore[misc]
                            f"{TRANSLATIONS[language]['file_too_many_columns_error'].format(cols=num_columns)}\n\n" +
                            f"{TRANSLATIONS[language]['file_format_guidance']}")
                        raise ValueError(TRANSLATIONS[language]['file_too_many_columns_error'].format(cols=num_columns))
                    elif num_columns not in [2, 3, 4]:
                        # Unexpected number of columns
                        messagebox.showerror(TRANSLATIONS[language]['file_read_error'],  # type: ignore[misc]
                            TRANSLATIONS[language]['file_columns_error_2_3_4'].format(delimiter=delimiter, line=i+2, cols=num_columns))
                        raise ValueError(TRANSLATIONS[language]['file_columns_error_2_3_4'].format(delimiter=delimiter, line=i+2, cols=num_columns))
                elif len(parts) != num_columns:
                    messagebox.showerror(TRANSLATIONS[language]['file_read_error'],  # type: ignore[misc]
                        TRANSLATIONS[language]['file_columns_inconsistent'].format(delimiter=delimiter, line=i+2, expected=num_columns, found=len(parts)))
                    raise ValueError(TRANSLATIONS[language]['file_columns_inconsistent'].format(delimiter=delimiter, line=i+2, expected=num_columns, found=len(parts)))
            
            # Load data using numpy
            dados: NDArray[np.str_] = np.genfromtxt(file_name, delimiter=delimiter, skip_header=1, dtype=str, encoding='utf-8')  # type: ignore
            dados = np.char.replace(dados, ',', '.')
            
            if num_columns == 2:
                # 2 columns: x, y (no uncertainties)
                x: NDArray[np.float64] = dados[:, 0].astype(np.float64)
                sigma_x: NDArray[np.float64] = np.zeros_like(x)  # No uncertainty in x
                y: NDArray[np.float64] = dados[:, 1].astype(np.float64)
                sigma_y: NDArray[np.float64] = np.zeros_like(y)  # No uncertainty in y
                preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})
            elif num_columns == 3:
                # 3 columns: x, y, sigma_y (no sigma_x)
                x = dados[:, 0].astype(np.float64)
                sigma_x = np.zeros_like(x)  # No uncertainty in x
                y = dados[:, 1].astype(np.float64)
                sigma_y = dados[:, 2].astype(np.float64)
                preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})
            else:
                # 4 columns: x, sigma_x, y, sigma_y
                x = dados[:, 0].astype(np.float64)
                sigma_x = dados[:, 1].astype(np.float64)
                y = dados[:, 2].astype(np.float64)
                sigma_y = dados[:, 3].astype(np.float64)
                preview_data = pd.DataFrame({'x': x, 'sigma_x': sigma_x, 'y': y, 'sigma_y': sigma_y})
            
            return x, sigma_x, y, sigma_y, preview_data
            
    except Exception as e:
        messagebox.showerror( # type: ignore[misc]
            TRANSLATIONS[language]['error'],
            TRANSLATIONS[language]['file_processing_error'].format(error=str(e))
        )
        raise


