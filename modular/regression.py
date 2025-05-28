"""Regression analysis module for AnaFis"""
from __future__ import annotations
import numpy as np
import sympy as sp
from scipy.odr import ODR, Model, RealData
import os
from typing import Tuple, List, Callable

from models import FloatArray

class RegressionAnalyzer:
    """Handles curve fitting and regression analysis"""
    def __init__(self) -> None:
        self.x: FloatArray | None = None
        self.y: FloatArray | None = None
        self.sigma_x: FloatArray | None = None
        self.sigma_y: FloatArray | None = None
        self.model: Callable | None = None
        self.parameters: List[sp.Symbol] = []
        self.header: List[str] = []
        self.language = 'en'  # Default language is English
        
    def read_file(self, file_name: str) -> Tuple[FloatArray, FloatArray, FloatArray, FloatArray]:
        """Read data from file"""
        error_messages = {
            'file_not_found': {
                'pt': f"O arquivo '{file_name}' não foi encontrado.",
                'en': f"The file '{file_name}' was not found."
            },
            'empty_file': {
                'pt': "O arquivo está vazio ou contém apenas o cabeçalho.",
                'en': "The file is empty or contains only the header."
            },
            'invalid_format': {
                'pt': "O arquivo deve ter 4 colunas separadas por '{delimiter}' (linha {line}).",
                'en': "The file must have 4 columns separated by '{delimiter}' (line {line})."
            },
            'unsupported_format': {
                'pt': "O formato do arquivo '{ext}' não é suportado.",
                'en': "The file format '{ext}' is not supported."
            }
        }

        if not os.path.isfile(file_name):
            raise FileNotFoundError(error_messages['file_not_found'][self.language])

        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        if ext in [".csv", ".txt"]:
            with open(file_name, 'r') as f:
                first_line = f.readline()
                delimiter = ';' if ';' in first_line else ','
                self.header = first_line.strip().split(delimiter)
                lines = f.readlines()

            if not lines:
                raise ValueError(error_messages['empty_file'][self.language])

            for i, line in enumerate(lines):
                parts = line.strip().split(delimiter)
                if len(parts) != 4:
                    raise ValueError(
                        error_messages['invalid_format'][self.language].format(delimiter=delimiter, line=i+2)
                    )

            data = np.genfromtxt(file_name, delimiter=delimiter, skip_header=1, dtype=str)
            data = np.char.replace(data, ',', '.')
            x = data[:, 0].astype(float)
            sigma_x = data[:, 1].astype(float)
            y = data[:, 2].astype(float)
            sigma_y = data[:, 3].astype(float)

        elif ext == ".json":
            import json
            with open(file_name, 'r') as f:
                json_data = json.load(f)

            try:
                x = np.array(json_data['x'], dtype=float)
                sigma_x = np.array(json_data['sigma_x'], dtype=float)
                y = np.array(json_data['y'], dtype=float)
                sigma_y = np.array(json_data['sigma_y'], dtype=float)
            except KeyError as e:
                raise ValueError(f"Missing key in JSON file: {e}")

        elif ext in [".xls", ".xlsx"]:
            import pandas as pd
            df = pd.read_excel(file_name)

            try:
                x = df['x'].to_numpy(dtype=float)
                sigma_x = df['sigma_x'].to_numpy(dtype=float)
                y = df['y'].to_numpy(dtype=float)
                sigma_y = df['sigma_y'].to_numpy(dtype=float)
            except KeyError as e:
                raise ValueError(f"Missing column in Excel file: {e}")

        else:
            raise ValueError(error_messages['unsupported_format'][self.language].format(ext=ext))

        return x, sigma_x, y, sigma_y

    def create_model(self, equation: str, parameters: List[sp.Symbol]) -> Tuple[Callable, List[Callable]]:
        """Create ODR model from equation"""
        x = sp.Symbol('x')
        expr = sp.sympify(equation)
        
        derivatives = [sp.diff(expr, p) for p in parameters]
        
        numeric_model = sp.lambdify((parameters, x), expr, 'numpy')
        numeric_derivatives = [sp.lambdify((parameters, x), d, 'numpy') for d in derivatives]
        
        return numeric_model, numeric_derivatives

    def perform_fit(self, initial_guess: List[float], max_iter: int = 1000):
        """Perform curve fitting"""
        if any(v is None for v in [self.x, self.y, self.sigma_x, self.sigma_y, self.model]):
            raise ValueError("Data or model not defined")
            
        assert self.model is not None
        assert self.x is not None
        assert self.y is not None
        assert self.sigma_x is not None
        assert self.sigma_y is not None
            
        odr_model = Model(self.model)
        data = RealData(self.x, self.y, sx=self.sigma_x, sy=self.sigma_y)
        odr = ODR(data, odr_model, beta0=initial_guess, maxit=max_iter)
        
        return odr.run()

    def calculate_statistics(self, result, y_pred: FloatArray) -> Tuple[float, float]:
        """Calculate goodness of fit statistics"""
        if any(v is None for v in [self.y, self.sigma_y]):
            raise ValueError("Data not defined")
            
        assert self.y is not None
        assert self.sigma_y is not None
            
        chi2_total = np.sum(((self.y - y_pred) / self.sigma_y) ** 2)
        r2 = 1 - np.sum((self.y - y_pred) ** 2) / np.sum((self.y - np.mean(self.y)) ** 2)
        
        return chi2_total, r2