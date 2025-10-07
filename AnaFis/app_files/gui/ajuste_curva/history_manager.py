"""History manager for curve fitting results"""

import tkinter as tk  # Added import for tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from app_files.utils.translations.api import get_string

if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame

    # Expected attributes on AjusteCurvaFrame for type checking:
    # last_result: Any  # Or a more specific type if available for fit result
    # last_chi2: Optional[float]
    # last_r2: Optional[float]
    # equacao: Optional[str]
    # parametros: Optional[List[Any]] # Or a more specific type for parameters
    # mostrar_resultados: Callable[[Any], None]


class HistoryManager:
    """Manages history of curve fitting results"""

    parent: "AjusteCurvaFrame"
    language: str
    history: List[Dict[str, Any]]
    history_index: int
    history_label: Optional[ttk.Label]
    prev_button: Optional[ttk.Button]
    next_button: Optional[ttk.Button]

    def __init__(self, parent_frame: "AjusteCurvaFrame", language: str = "pt") -> None:
        """Initialize the history manager

        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this manager
            language: Interface language
        """
        self.parent = parent_frame
        self.language = language

        # History state
        self.history = []
        self.history_index = -1

        # UI elements
        self.history_label = None
        self.prev_button = None
        self.next_button = None

    def setup_ui(
        self, parent_widget: tk.Widget
    ) -> None:  # Changed parent_frame to parent_widget and type to tk.Widget
        """Set up history navigation UI

        Args:
            parent_widget: Parent frame for the history widgets
        """  # History navigation frame
        nav_frame = ttk.Frame(parent_widget)
        nav_frame.grid(row=0, column=0, sticky="ew", pady=5)

        prev_button_text = get_string("history", "previous_button", self.language)
        self.prev_button = ttk.Button(
            nav_frame, text=prev_button_text, command=self.prev_fit
        )
        self.prev_button.grid(row=0, column=0, padx=2)

        next_button_text = get_string("history", "next_button", self.language)
        self.next_button = ttk.Button(
            nav_frame, text=next_button_text, command=self.next_fit
        )
        self.next_button.grid(row=0, column=1, padx=2)

        history_label_text = get_string(
            "history", "history_label_initial", self.language
        )
        self.history_label = ttk.Label(nav_frame, text=history_label_text)
        self.history_label.grid(row=0, column=2, padx=10, sticky="w")

    def switch_language(self, language: str) -> None:
        """Switch language for history UI elements."""
        self.language = language
        # Update button texts if they exist
        if getattr(self, "prev_button", None) is not None:
            try:
                self.prev_button.config(text=get_string("history", "previous_button", self.language))
            except Exception:
                pass
        if getattr(self, "next_button", None) is not None:
            try:
                self.next_button.config(text=get_string("history", "next_button", self.language))
            except Exception:
                pass
        # Update label text
        if getattr(self, "history_label", None) is not None:
            try:
                # If history is empty use initial label, otherwise updated label
                if len(self.history) == 0:
                    label_text = get_string("history", "history_label_initial", self.language)
                else:
                    label_text = get_string("history", "history_label_updated", self.language)
                # If updated label needs formatting, try to format; otherwise set directly
                try:
                    total = len(self.history)
                    current = self.history_index + 1 if total > 0 else 0
                    self.history_label.config(text=label_text.format(current=current, total=total))
                except Exception:
                    self.history_label.config(text=label_text)
            except Exception:
                pass

    # Note: layout column weight configuration is handled where nav_frame is created

    def add_fit_result(
        self,
        result: Any,
        chi2: Optional[float],
        r2: Optional[float],
        equation: Optional[str],
        parameters: Optional[List[Any]],
    ) -> None:
        """Add a new fit result to history

        Args:
            result: The fit result object
            chi2: Chi-squared value
            r2: R-squared value
            equation: The equation used for the fit
            parameters: List of parameters
        """
        fit_data: Dict[str, Any] = {
            "result": result,
            "chi2": chi2,
            "r2": r2,
            "equation": equation,
            "parameters": parameters,
        }
        # If new result is added after navigating back, truncate future history
        if self.history_index < len(self.history) - 1:
            self.history = self.history[: self.history_index + 1]

        self.history.append(fit_data)
        self.history_index = len(self.history) - 1
        self.update_history_label()
        # Update parent with the new result as it's the current one
        self.apply_fit_from_history(
            update_plot_and_results=False
        )  # Avoid re-plotting if parent already did

    def prev_fit(self) -> None:
        """Navigate to previous fit in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.apply_fit_from_history()

    def next_fit(self) -> None:
        """Navigate to next fit in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.apply_fit_from_history()

    def apply_fit_from_history(self, update_plot_and_results: bool = True) -> None:
        """Apply fit from history.

        Args:
            update_plot_and_results: If True, tells parent to update plot and results display.
                                     Set to False if parent is already handling this.
        """
        if 0 <= self.history_index < len(self.history):
            fit_data = self.history[self.history_index]

            # Update parent with historical data
            self.parent.last_result = fit_data["result"]
            self.parent.last_chi2 = fit_data["chi2"]
            self.parent.last_r2 = fit_data["r2"]
            self.parent.equacao = fit_data["equation"]
            self.parent.parametros = fit_data["parameters"]

            if update_plot_and_results:
                # Display results - parent should handle the actual display logic
                self.parent.mostrar_resultados(self.parent.last_result)

            self.update_history_label()

    def update_history_label(self) -> None:
        """Update history navigation label"""
        if self.history_label:
            total = len(self.history)
            current = self.history_index + 1 if total > 0 else 0
            history_label_text = get_string(
                "history", "history_label_updated", self.language
            )
            self.history_label.config(
                text=history_label_text.format(current=current, total=total)
            )
