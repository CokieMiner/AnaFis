import pytest
from app_files.gui.ajuste_curva_gui import AjusteCurvaGUI
from app_files.gui.calculo_incertezas_gui import CalculoIncertezasGUI
import tkinter as tk

def test_ajuste_curva_gui_instantiation():
    root = tk.Tk()
    gui = AjusteCurvaGUI(root, language='en')
    assert gui is not None
    root.destroy()

def test_calculo_incertezas_gui_instantiation():
    root = tk.Tk()
    gui = CalculoIncertezasGUI(root, language='en')
    assert gui is not None
    root.destroy()
