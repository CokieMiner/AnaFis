"""Main application module"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from app_files.gui.ajuste_curva.main_gui import AjusteCurvaGUI
from app_files.gui.incerteza.calculo_incertezas_gui import CalculoIncertezasGUI
from app_files.utils.constants import TRANSLATIONS


class AplicativoUnificado:
    """Main application class"""
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.language = 'pt'  # Default language
        self.root.title(TRANSLATIONS[self.language]['app_title'])
        self.root.geometry("400x300")
        self._windows: dict[str, tk.Toplevel] = {}
        self.create_main_menu()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_main_menu(self) -> None:
        """Create main menu"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        ttk.Label(
            main_frame,
            text=TRANSLATIONS[self.language]['app_title'],
            font=('Helvetica', 16)
        ).grid(row=0, column=0, pady=20, sticky="ew")

        ttk.Button(
            main_frame,
            text=TRANSLATIONS[self.language]['curve_fitting'],
            command=self.open_curve_fitting
        ).grid(row=1, column=0, pady=5, sticky="ew")

        ttk.Button(
            main_frame,
            text=TRANSLATIONS[self.language]['uncertainty_calc'],
            command=self.open_uncertainty_calc
        ).grid(row=2, column=0, pady=5, sticky="ew")

        ttk.Button(
            main_frame,
            text=TRANSLATIONS[self.language]['exit'],
            command=self.root.quit
        ).grid(row=3, column=0, pady=20, sticky="ew")

        # Language switcher
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=4, column=0, pady=10, sticky="ew")
        ttk.Label(lang_frame, text=TRANSLATIONS[self.language]['language_label']).grid(row=0, column=0, padx=5)
        lang_selector = ttk.Combobox(lang_frame, values=['pt', 'en'], state="readonly", width=5)
        lang_selector.set(self.language)
        lang_selector.grid(row=0, column=1, padx=5)
        lang_selector.bind('<<ComboboxSelected>>', lambda e: self.switch_language(lang_selector.get()))

    def switch_language(self, lang: str) -> None:
        """Switch application language"""
        self.language = lang
        self.root.title(TRANSLATIONS[self.language]['app_title'])
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_main_menu()
        # Update open windows
        for key, window in self._windows.items():
            if key == 'curve_fitting':
                window.title(TRANSLATIONS[self.language]['curve_fitting_title'])
            elif key == 'uncertainty_calc':
                window.title(TRANSLATIONS[self.language]['uncertainty_calc'])

    def _close_window(self, window_key: str) -> None:
        """Handle window closing"""
        if window_key in self._windows:
            self._windows[window_key].destroy()
            del self._windows[window_key]
        if not self._windows:
            self.root.deiconify()

    def open_curve_fitting(self) -> None:
        """Open curve fitting window"""
        if 'curve_fitting' not in self._windows:
            self.root.withdraw()
            window = tk.Toplevel(self.root)
            window.title(TRANSLATIONS[self.language]['curve_fitting_title'])
            def on_close():
                self._close_window('curve_fitting')
                self.root.deiconify()
            window.protocol("WM_DELETE_WINDOW", on_close)
            AjusteCurvaGUI(window, self.language)
            self._windows['curve_fitting'] = window
        else:
            self._windows['curve_fitting'].lift()

    def open_uncertainty_calc(self) -> None:
        """Open uncertainty calculation window"""
        if 'uncertainty_calc' not in self._windows:
            self.root.withdraw()
            window = tk.Toplevel(self.root)
            window.title(TRANSLATIONS[self.language]['uncertainty_calc'])
            def on_close():
                self._close_window('uncertainty_calc')
                self.root.deiconify()
            window.protocol("WM_DELETE_WINDOW", on_close)
            CalculoIncertezasGUI(window, self.language)
            self._windows['uncertainty_calc'] = window
        else:
            self._windows['uncertainty_calc'].lift()

    def on_close(self) -> None:
        """Handle application close"""
        # Close all child windows
        for window in list(self._windows.values()):
            try:
                window.destroy()
            except:
                pass
        self._windows.clear()
        self.root.quit()
        self.root.destroy()

    def run(self) -> None:
        """Start the application"""
        self.root.mainloop()