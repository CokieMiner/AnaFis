"""AnaFis main application module"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from .gui import AjusteCurvaGUI, CalculoIncertezasGUI

class AplicativoUnificado:
    """Main application class"""
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Análise de Dados Físicos")
        self.root.geometry("400x300")
        self._windows: dict[str, tk.Toplevel] = {}
        self.criar_menu_principal()

    def criar_menu_principal(self) -> None:
        """Create main menu"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        ttk.Label(
            main_frame,
            text="Análise de Dados Físicos",
            font=('Helvetica', 16)
        ).grid(row=0, column=0, pady=20, sticky="ew")

        # Buttons
        ttk.Button(
            main_frame,
            text="Ajuste de Curvas",
            command=self.abrir_ajuste_curvas
        ).grid(row=1, column=0, pady=10, sticky="ew")

        ttk.Button(
            main_frame,
            text="Cálculo de Incertezas",
            command=self.abrir_calculo_incertezas
        ).grid(row=2, column=0, pady=10, sticky="ew")

        ttk.Button(
            main_frame,
            text="Sair",
            command=self.root.quit
        ).grid(row=3, column=0, pady=20, sticky="ew")

    def abrir_ajuste_curvas(self) -> None:
        """Open curve fitting window"""
        if 'ajuste' not in self._windows:
            window = tk.Toplevel(self.root)
            self._windows['ajuste'] = window
            AjusteCurvaGUI(window)
            window.protocol(
                "WM_DELETE_WINDOW",
                lambda: self._fechar_janela('ajuste')
            )

    def abrir_calculo_incertezas(self) -> None:
        """Open uncertainty calculation window"""
        if 'incertezas' not in self._windows:
            window = tk.Toplevel(self.root)
            self._windows['incertezas'] = window
            CalculoIncertezasGUI(window)
            window.protocol(
                "WM_DELETE_WINDOW",
                lambda: self._fechar_janela('incertezas')
            )

    def _fechar_janela(self, window_key: str) -> None:
        """Close window and cleanup"""
        if window_key in self._windows:
            self._windows[window_key].destroy()
            del self._windows[window_key]
            
    def run(self) -> None:
        """Start the application"""
        self.root.mainloop()