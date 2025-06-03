"""
AnaFis GUI package
"""
# Use a more direct import
import sys
from app_files.gui.ajuste_curva.main_gui import AjusteCurvaGUI as _AjusteCurvaGUI

# Re-export the class
AjusteCurvaGUI = _AjusteCurvaGUI

__all__ = ['AjusteCurvaGUI']
