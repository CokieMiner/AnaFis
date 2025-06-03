"""AnaFis - Análise de Dados Físicos

A Python package for physics data analysis, curve fitting and uncertainty calculations.
"""

__version__ = "7.0.0"
__author__ = "Pedro"

# Import from the new modular structure
from app_files.gui.ajuste_curva.models import ODRModel, ODRModelImplementation, ProgressTracker
from app_files.gui.ajuste_curva.regression import RegressionAnalyzer
from app_files.gui.incerteza.uncertainties import UncertaintyCalculator
from app_files.gui.ajuste_curva.main_gui import AjusteCurvaGUI
from app_files.gui.incerteza.calculo_incertezas_gui import CalculoIncertezasGUI
from app_files.main import AplicativoUnificado

__all__ = [
    "ODRModel", "ODRModelImplementation", "ProgressTracker",
    "RegressionAnalyzer", "UncertaintyCalculator",
    "AjusteCurvaGUI", "CalculoIncertezasGUI",
    "AplicativoUnificado"
]