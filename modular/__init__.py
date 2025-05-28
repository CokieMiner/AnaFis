"""AnaFis - Análise de Dados Físicos

A Python package for physics data analysis, curve fitting and uncertainty calculations.
"""

from .models import ODRModel, ODRModelImplementation, ProgressTracker
from .regression import RegressionAnalyzer
from .uncertainties import UncertaintyCalculator
from .gui import AjusteCurvaGUI, CalculoIncertezasGUI
from .main import AplicativoUnificado

__version__ = "7.0.0"
__author__ = "Pedro"

__all__ = [
    "ODRModel", "ODRModelImplementation", "ProgressTracker",
    "RegressionAnalyzer", "UncertaintyCalculator",
    "AjusteCurvaGUI", "CalculoIncertezasGUI",
    "AplicativoUnificado"
]