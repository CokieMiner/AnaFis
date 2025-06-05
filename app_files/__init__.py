"""AnaFis - Análise de Dados Físicos

A Python package for physics data analysis, curve fitting and uncertainty calculations.
"""

__version__ = "9"
__author__ = "CokieMiner"

# Import from the new modular structure
from app_files.gui.ajuste_curva.models import ODRModel, ODRModelImplementation, ProgressTracker
from app_files.gui.incerteza.uncertainties import UncertaintyCalculator
from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
from app_files.gui.incerteza.calculo_incertezas_gui import CalculoIncertezasFrame
from app_files.main import AplicativoUnificado

__all__ = [
    "ODRModel", "ODRModelImplementation", "ProgressTracker",
    "UncertaintyCalculator",
    "AjusteCurvaFrame", "CalculoIncertezasFrame",
    "AplicativoUnificado"
]