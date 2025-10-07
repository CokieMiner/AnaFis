"""Advanced configuration dialog for curve fitting"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional
import logging

from app_files.utils.translations.api import get_string

# Lazy import utility
from app_files.utils.lazy_loader import lazy_import
# Error handler import (assume it's in utils or startup)
from app_files.utils import error_handler
# Import for type hints only
if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
    from app_files.gui.ajuste_curva.adjustment_points_manager import (
        AdjustmentPointsManager,
    )
    from app_files.gui.ajuste_curva.parameter_estimates_manager import (
        ParameterEstimatesManager,
    )
    from app_files.gui.ajuste_curva.custom_function_manager import CustomFunctionManager


class AdvancedConfigDialog:
    """Dialog for advanced configuration options"""

    def __init__(
        self,
        parent_frame: "AjusteCurvaFrame",
        custom_function_manager: Optional["CustomFunctionManager"],
        parameter_estimates_manager: Optional["ParameterEstimatesManager"],
        adjustment_points_manager: Optional["AdjustmentPointsManager"],
        language: str = "pt",
    ) -> None:
        """
        Initialize the advanced configuration dialog

        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this dialog
            custom_function_manager: Manager for custom functions
            parameter_estimates_manager: Manager for parameter estimates
            adjustment_points_manager: Manager for adjustment points
            language: Interface language
        """

        self.parent = parent_frame
        self.language = language
        self.dialog = None
        self.custom_function_manager = custom_function_manager
        self.parameter_estimates_manager = parameter_estimates_manager
        self.adjustment_points_manager = adjustment_points_manager  # Store the manager
        self.popup_window: Optional[tk.Toplevel] = None  # For theme updates

    def show_dialog(self) -> None:
        """Show the advanced configuration dialog"""
        theme_manager = lazy_import("app_files.utils.theme_manager", "theme_manager")
        # Create a new top-level window
        popup = tk.Toplevel(self.parent.parent)
        popup.title(
            get_string(
                "ajuste_curva",
                "advanced_config",
                self.language,
                fallback="Configuração avançada",
            )
        )
        popup.geometry("620x670")
        popup.resizable(True, True)
        # Apply theme-adaptive background
        popup.configure(bg=theme_manager.get_adaptive_color("background"))

        # Store reference to popup for theme updates
        self.popup_window = popup

        # Register for theme change callbacks
        theme_manager.register_color_callback(self._update_popup_colors)

        # Fix the transient call by checking if parent is a window
        if isinstance(self.parent.parent, (tk.Tk, tk.Toplevel)):
            popup.transient(self.parent.parent)  # Make it a child of main window

        popup.grab_set()  # Make it modal

        # Create a notebook for tabs
        notebook = ttk.Notebook(popup)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # === First tab: Adjustment Points ===
        adjust_tab = ttk.Frame(notebook)
        notebook.add(
            adjust_tab,
            text=get_string(
                "ajuste_curva",
                "adjustment_points",
                self.language,
                fallback="Pontos de ajuste",
            ),
        )

        # Configure grid weights to maximize scrollbox space
        adjust_tab.columnconfigure(0, weight=1)
        adjust_tab.rowconfigure(1, weight=1)  # Make the row with scrollbox expandable

        # Set up the adjustment points UI with expanded scrollbox
        if self.adjustment_points_manager is None:
            logging.error("adjustment_points_manager is None, cannot set up UI")
            error_handler.handle_error(
                get_string("ajuste_curva", "error", self.language, fallback="Erro"),
                get_string(
                    "ajuste_curva",
                    "config_error_adjust_manager",
                    self.language,
                    fallback="Erro ao configurar o gerenciador de pontos de ajuste.",
                ),
            )
            return

        self.adjustment_points_manager.setup_ui(adjust_tab, maximize_scrollbox=True)

        # === Second tab: Initial Estimates ===
        estimates_tab = ttk.Frame(notebook)
        notebook.add(
            estimates_tab,
            text=get_string(
                "ajuste_curva",
                "initial_estimates",
                self.language,
                fallback="Estimativas iniciais",
            ),
        )

        # Add a safety check before calling setup_ui
        if self.parameter_estimates_manager is None:
            logging.error("parameter_estimates_manager is None, cannot set up UI")
            error_handler.handle_error(
                get_string("ajuste_curva", "error", self.language, fallback="Erro"),
                get_string(
                    "ajuste_curva",
                    "config_error_param_manager",
                    self.language,
                    fallback="Erro ao configurar o gerenciador de parâmetros.",
                ),
            )
            return

        # Set up the parameter estimates UI
        self.parameter_estimates_manager.setup_ui(estimates_tab)

        # === Third tab: Custom Functions ===
        funcs_tab = ttk.Frame(notebook)
        notebook.add(
            funcs_tab,
            text=get_string(
                "ajuste_curva",
                "custom_functions",
                self.language,
                fallback="Funções personalizadas",
            ),
        )

        # Configure grid weights for custom functions tab
        funcs_tab.columnconfigure(0, weight=1)
        funcs_tab.rowconfigure(1, weight=1)  # Make the row with scrollbox expandable

        # Set up the custom functions UI with expanded scrollbox
        if self.custom_function_manager is None:
            logging.error("custom_function_manager is None, cannot set up UI")
            error_handler.handle_error(
                get_string("ajuste_curva", "error", self.language, fallback="Erro"),
                get_string(
                    "ajuste_curva",
                    "config_error_custom_func",
                    self.language,
                    fallback="Erro ao configurar funções personalizadas.",
                ),
            )
            return

        self.custom_function_manager.setup_ui(funcs_tab, maximize_scrollbox=True)

        # Function to handle popup closing
        def on_close() -> None:
            # Save adjustment points when closing
            if self.adjustment_points_manager is not None:
                self.adjustment_points_manager.save_points()
            # Save custom functions
            if self.custom_function_manager is not None:
                self.custom_function_manager.save_functions()
            # Destroy the popup
            popup.destroy()

        # Button to close the popup - now calls our custom close function
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10, fill="x")

        close_button = ttk.Button(
            button_frame,
            text=get_string("ajuste_curva", "close", self.language, fallback="Fechar"),
            command=on_close,
        )
        close_button.pack(anchor="center")

        # Also handle window close via X button
        popup.protocol("WM_DELETE_WINDOW", on_close)

        # Center the popup on the parent window
        popup.update_idletasks()
        parent_window = self.parent.parent
        x = (
            parent_window.winfo_x()
            + (parent_window.winfo_width() // 2)
            - (popup.winfo_width() // 2)
        )
        y = (
            parent_window.winfo_y()
            + (parent_window.winfo_height() // 2)
            - (popup.winfo_height() // 2)
        )
        popup.geometry(f"+{x}+{y}")

    def _update_popup_colors(self) -> None:
        """Update popup colors when theme changes"""
        try:
            if (
                hasattr(self, "popup_window")
                and self.popup_window is not None
                and self.popup_window.winfo_exists()
            ):
                theme_manager = lazy_import(
                    "app_files.utils.theme_manager", "theme_manager"
                )
                bg_color = theme_manager.get_adaptive_color("background")
                self.popup_window.configure(bg=bg_color)
                logging.debug("Advanced config dialog colors updated for theme change")
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Justification: Theme update should never crash the app
            logging.warning("Failed to update advanced config dialog colors: %s", e)

    def switch_language(self, language: str) -> None:
        """Update language for the dialog. If the popup is open, update its texts."""
        self.language = language
        try:
            if (
                hasattr(self, "popup_window")
                and self.popup_window is not None
                and self.popup_window.winfo_exists()
            ):
                popup = self.popup_window
                # Update title
                try:
                    popup.title(
                        get_string(
                            "ajuste_curva",
                            "advanced_config",
                            self.language,
                            fallback="Configuração avançada",
                        )
                    )
                except Exception:
                    pass

                # Update notebook tab labels (if any)
                try:
                    for child in popup.winfo_children():
                        if isinstance(child, ttk.Notebook):
                            notebook = child
                            for idx in range(notebook.index("end")):
                                tab_text = notebook.tab(idx, option="text")
                                # Map known tabs
                                if tab_text in [
                                    get_string("ajuste_curva", "adjustment_points", "pt"),
                                    get_string("ajuste_curva", "adjustment_points", "en"),
                                ]:
                                    notebook.tab(idx, text=get_string("ajuste_curva", "adjustment_points", self.language))
                                elif tab_text in [
                                    get_string("ajuste_curva", "initial_estimates", "pt"),
                                    get_string("ajuste_curva", "initial_estimates", "en"),
                                ]:
                                    notebook.tab(idx, text=get_string("ajuste_curva", "initial_estimates", self.language))
                                elif tab_text in [
                                    get_string("ajuste_curva", "custom_functions", "pt"),
                                    get_string("ajuste_curva", "custom_functions", "en"),
                                ]:
                                    notebook.tab(idx, text=get_string("ajuste_curva", "custom_functions", self.language))
                except Exception:
                    pass

                # Update close button text if present
                try:
                    for child in popup.winfo_children():
                        for sub in child.winfo_children():
                            if isinstance(sub, ttk.Button):
                                # Update the close button specifically by checking its current text
                                if sub.cget("text") in [
                                    get_string("ajuste_curva", "close", "pt"),
                                    get_string("ajuste_curva", "close", "en"),
                                ]:
                                    sub.config(text=get_string("ajuste_curva", "close", self.language))
                except Exception:
                    pass

                # Propagate to managers inside the dialog if they implement switch_language
                try:
                    if self.adjustment_points_manager and hasattr(self.adjustment_points_manager, "switch_language"):
                        self.adjustment_points_manager.switch_language(self.language)
                except Exception:
                    pass
                try:
                    if self.parameter_estimates_manager and hasattr(self.parameter_estimates_manager, "switch_language"):
                        self.parameter_estimates_manager.switch_language(self.language)
                except Exception:
                    pass
                try:
                    if self.custom_function_manager and hasattr(self.custom_function_manager, "switch_language"):
                        self.custom_function_manager.switch_language(self.language)
                except Exception:
                    pass
        except Exception:
            logging.exception("Failed to switch language on AdvancedConfigDialog")
