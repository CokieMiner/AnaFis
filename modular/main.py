"""AnaFis main application module"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from .gui import AjusteCurvaGUI, CalculoIncertezasGUI

class AplicativoUnificado:
    """Main application class"""
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.language = 'pt'  # Default language is Portuguese
        self.translations = {
            'pt': {
                'title': 'Análise de Dados Físicos',
                'curve_fitting': 'Ajuste de Curvas',
                'uncertainty_calc': 'Cálculo de Incertezas',
                'exit': 'Sair'
            },
            'en': {
                'title': 'Physics Data Analysis',
                'curve_fitting': 'Curve Fitting',
                'uncertainty_calc': 'Uncertainty Calculation',
                'exit': 'Exit'
            }
        }
        self.root.title(self.translations[self.language]['title'])
        self.root.geometry("400x300")
        self._windows: dict[str, tk.Toplevel] = {}
        self.create_main_menu()

    def create_main_menu(self) -> None:
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
            text=self.translations[self.language]['title'],
            font=('Helvetica', 16)
        ).grid(row=0, column=0, pady=20, sticky="ew")

        # Buttons
        ttk.Button(
            main_frame,
            text=self.translations[self.language]['curve_fitting'],
            command=self.open_curve_fitting
        ).grid(row=1, column=0, pady=10, sticky="ew")

        ttk.Button(
            main_frame,
            text=self.translations[self.language]['uncertainty_calc'],
            command=self.open_uncertainty_calc
        ).grid(row=2, column=0, pady=10, sticky="ew")

        ttk.Button(
            main_frame,
            text=self.translations[self.language]['exit'],
            command=self.root.quit
        ).grid(row=3, column=0, pady=20, sticky="ew")

        # Language switcher
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=4, column=0, pady=10, sticky="ew")
        ttk.Label(lang_frame, text="Language:").grid(row=0, column=0, padx=5)
        lang_selector = ttk.Combobox(lang_frame, values=['pt', 'en'], state="readonly", width=5)
        lang_selector.set(self.language)
        lang_selector.grid(row=0, column=1, padx=5)
        lang_selector.bind('<<ComboboxSelected>>', lambda e: self.switch_language(lang_selector.get()))

    def switch_language(self, lang: str) -> None:
        """Switch application language"""
        self.language = lang
        self.root.title(self.translations[self.language]['title'])
        self.create_main_menu()

    def open_curve_fitting(self) -> None:
        """Open curve fitting window"""
        if 'curve_fitting' not in self._windows:
            window = tk.Toplevel(self.root)
            self._windows['curve_fitting'] = window
            AjusteCurvaGUI(window, self.language)  # Ensure language is passed correctly
            window.protocol(
                "WM_DELETE_WINDOW",
                lambda: self._close_window('curve_fitting')
            )

    def open_uncertainty_calc(self) -> None:
        """Open uncertainty calculation window"""
        if 'uncertainty_calc' not in self._windows:
            window = tk.Toplevel(self.root)
            self._windows['uncertainty_calc'] = window
            CalculoIncertezasGUI(window)  # Removed language argument as it is not expected
            window.protocol(
                "WM_DELETE_WINDOW",
                lambda: self._close_window('uncertainty_calc')
            )

    def _close_window(self, window_key: str) -> None:
        """Close window and cleanup"""
        if window_key in self._windows:
            self._windows[window_key].destroy()
            del self._windows[window_key]
            
    def run(self) -> None:
        """Start the application"""
        self.root.mainloop()