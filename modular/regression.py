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
        self.modelo: Callable | None = None
        self.parametros: List[sp.Symbol] = []
        self.cabecalho: List[str] = []
        
    def ler_arquivo(self, nome_arquivo: str) -> Tuple[FloatArray, FloatArray, FloatArray, FloatArray]:
        """Read data from file"""
        if not os.path.isfile(nome_arquivo):
            raise FileNotFoundError(f"O arquivo '{nome_arquivo}' não foi encontrado.")
            
        _, ext = os.path.splitext(nome_arquivo)
        delimiter = ',' if ext.lower() == ".csv" else '\t'

        with open(nome_arquivo, 'r') as f:
            self.cabecalho = f.readline().strip().split(delimiter)
            lines = f.readlines()
            
        if not lines:
            raise ValueError("O arquivo está vazio ou só contém o cabeçalho.")

        # Validate data format
        for i, line in enumerate(lines):
            parts = line.strip().split(delimiter)
            if len(parts) != 4:
                raise ValueError(
                    f"O arquivo precisa ter 4 colunas separadas por '{delimiter}' (linha {i+2})."
                )

        # Load data using numpy
        dados = np.genfromtxt(nome_arquivo, delimiter=delimiter, skip_header=1, dtype=str)
        dados = np.char.replace(dados, ',', '.')
        x = dados[:, 0].astype(float)
        sigma_x = dados[:, 1].astype(float)
        y = dados[:, 2].astype(float)
        sigma_y = dados[:, 3].astype(float)
        
        return x, sigma_x, y, sigma_y

    def criar_modelo(self, equacao: str, parametros: List[sp.Symbol]) -> Tuple[Callable, List[Callable]]:
        """Create ODR model from equation"""
        x = sp.Symbol('x')
        expr = sp.sympify(equacao)
        
        derivadas = [sp.diff(expr, p) for p in parametros]
        
        modelo_numerico = sp.lambdify((parametros, x), expr, 'numpy')
        derivadas_numericas = [sp.lambdify((parametros, x), d, 'numpy') for d in derivadas]
        
        return modelo_numerico, derivadas_numericas

    def realizar_ajuste(self, chute: List[float], max_iter: int = 1000):
        """Perform curve fitting"""
        if any(v is None for v in [self.x, self.y, self.sigma_x, self.sigma_y, self.modelo]):
            raise ValueError("Dados ou modelo não definidos")
            
        assert self.modelo is not None
        assert self.x is not None
        assert self.y is not None
        assert self.sigma_x is not None
        assert self.sigma_y is not None
            
        modelo_odr = Model(self.modelo)
        dados = RealData(self.x, self.y, sx=self.sigma_x, sy=self.sigma_y)
        odr = ODR(dados, modelo_odr, beta0=chute, maxit=max_iter)
        
        return odr.run()

    def calcular_estatisticas(self, resultado, y_pred: FloatArray) -> Tuple[float, float]:
        """Calculate goodness of fit statistics"""
        if any(v is None for v in [self.y, self.sigma_y]):
            raise ValueError("Dados não definidos")
            
        assert self.y is not None
        assert self.sigma_y is not None
            
        chi2_total = np.sum(((self.y - y_pred) / self.sigma_y) ** 2)
        r2 = 1 - np.sum((self.y - y_pred) ** 2) / np.sum((self.y - np.mean(self.y)) ** 2)
        
        return chi2_total, r2