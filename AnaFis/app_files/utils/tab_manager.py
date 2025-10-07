"""TabManager module for managing notebook tabs and close logic."""

import time
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Tuple, Literal, Protocol, Optional, TypedDict, cast, Any
from app_files.utils.translations.api import get_string
from app_files.utils.lazy_loader import lazy_import
from app_files.utils.error_handler import show_error


# Type aliases for better type safety
TabType = Literal["curve_fitting", "uncertainty_calc", "home", "settings"]


class TabInstanceProtocol(Protocol):
    """Defines the interface for tab instances managed by TabManager."""

    def switch_language(self, language: str) -> None:
        """Switch the language of the tab instance."""

    def cleanup(self) -> None:
        """Cleanup resources held by the tab instance."""

    def on_tab_activated(self) -> None:
        """Callback for when the tab is activated."""


class TabData(TypedDict):
    """TypedDict for tab metadata managed by TabManager."""

    widget: ttk.Frame
    instance: Optional[TabInstanceProtocol]
    tab_type: TabType
    created_time: float


class TabManager:
    """Manages tabs and close button logic for a ttk.Notebook."""

    def __init__(
        self,
        notebook: ttk.Notebook,
        home_tab: ttk.Frame,
        open_tabs: Dict[str, TabData],
        language: str,
    ):
        """Initialize TabManager.
        Args:
            notebook: The ttk.Notebook instance.
            home_tab: The home tab frame.
            open_tabs: Currently open tabs data.
            language: Current language code.
        """
        self.notebook = notebook
        self.home_tab = home_tab
        self.open_tabs = open_tabs
        self.language = language

    def add_close_button_to_tab(self, tab_main_frame: ttk.Frame) -> ttk.Frame:
        """Adds a standardized header with a close button to the given tab_main_frame.
        Returns a new frame within tab_main_frame where the actual tab content should be placed.
        """
        if hasattr(tab_main_frame, "app_content_container"):
            return getattr(tab_main_frame, "app_content_container")
        app_header_frame = ttk.Frame(tab_main_frame)
        app_header_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        app_close_button = ttk.Button(
            app_header_frame,
            text="X",
            width=2,
            command=lambda tmf=tab_main_frame: self.close_tab_by_widget(tmf),
        )
        app_close_button.pack(side=tk.RIGHT, padx=2, pady=2)
        app_content_container = ttk.Frame(tab_main_frame)
        app_content_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        setattr(tab_main_frame, "app_header_frame", app_header_frame)
        setattr(tab_main_frame, "app_close_button", app_close_button)
        setattr(tab_main_frame, "app_content_container", app_content_container)
        return app_content_container

    def close_tab_by_widget(self, tab_frame: tk.Widget) -> None:
        """Find the tab index for the given widget and close it."""
        try:
            _tab_ids_tuple: Tuple[str, ...] = tuple(self.notebook.tabs())
            tabs_list: List[str] = list(_tab_ids_tuple) if _tab_ids_tuple else []
            for i, tab_id_str in enumerate(tabs_list):
                widget = cast(ttk.Frame, self.notebook.nametowidget(tab_id_str))
                if widget == tab_frame:
                    self.close_tab_at_index(i)
                    return
            logging.warning("Could not find tab to close: %s", tab_frame)
        except (tk.TclError, AttributeError) as e:
            logging.error("Error finding tab to close: %s", e)

    def close_tab_at_index(self, index: int) -> None:
        """Close a tab at a specific index."""
        try:
            _current_tabs_tuple: Tuple[str, ...] = tuple(self.notebook.tabs())
            current_tabs_raw: Tuple[str, ...] = _current_tabs_tuple
            current_tabs_list: List[str] = (
                list(current_tabs_raw) if current_tabs_raw else []
            )
            if not current_tabs_list or index >= len(current_tabs_list):
                logging.warning("Tab index %d out of range.", index)
                return
            tab_to_check_name = current_tabs_list[index]
            widget_to_check = cast(
                ttk.Frame, self.notebook.nametowidget(tab_to_check_name)
            )
            if index == 0 and widget_to_check == self.home_tab:
                return
            tab_widget_to_close = widget_to_check
            tab_key_to_delete = None
            instance_to_cleanup = None
            for key, tab_data_entry in self.open_tabs.items():
                if tab_data_entry.get("widget") == tab_widget_to_close:
                    tab_key_to_delete = key
                    instance_to_cleanup = tab_data_entry.get("instance")
                    break
            if instance_to_cleanup and hasattr(instance_to_cleanup, "cleanup"):
                try:
                    instance_to_cleanup.cleanup()
                except (AttributeError, RuntimeError) as e:
                    logging.error(
                        "Error in tab cleanup for %s: %s", tab_key_to_delete, e
                    )
            if tab_key_to_delete:
                del self.open_tabs[tab_key_to_delete]
            else:
                logging.warning(
                    "Tab at index %d (widget: %s) not found in open_tabs tracking.",
                    index,
                    tab_widget_to_close,
                )
            self.notebook.forget(index)
        except (tk.TclError, ValueError, KeyError, IndexError) as e:
            logging.error("Error closing tab at index %d: %s", index, e)

    def monitor_tabs(self):
        """Periodically check tabs to ensure close buttons are visible."""
        _tab_ids_tuple = self.notebook.tabs()
        tab_ids_raw = cast(Tuple[str, ...], _tab_ids_tuple)
        tabs_list: List[str] = list(tab_ids_raw) if tab_ids_raw else []
        for i, tab_id_str in enumerate(tabs_list):
            if i > 0:  # Skip home tab
                tab_frame = cast(ttk.Frame, self.notebook.nametowidget(tab_id_str))
                app_close_button = getattr(tab_frame, "app_close_button", None)
                if not (app_close_button and app_close_button.winfo_exists()):
                    self.add_close_button_to_tab(tab_frame)
        self.notebook.after(1000, self.monitor_tabs)

    def create_home_tab(self, home_tab: ttk.Frame) -> None:
        """Register the home tab in open_tabs."""
        self.open_tabs["home"] = {
            "widget": home_tab,
            "instance": None,
            "tab_type": "home",
            "created_time": 0.0,
        }

    def open_curve_fitting_tab(self) -> None:
        """Open a new curve fitting tab using the translation API."""
        # pylint: disable=invalid-name
        AjusteCurvaFrame = lazy_import(
            "app_files.gui.ajuste_curva.main_gui",
            "AjusteCurvaFrame",
            preload_priority=5,
            dependencies=["numpy", "matplotlib"],
        )
        i = 1
        while f"curve_fitting_{i}" in self.open_tabs:
            i += 1
        tab_key = f"curve_fitting_{i}"
        tab_main_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            tab_main_frame, text=get_string("curve_fitting", "tab_title", self.language)
        )
        content_area = self.add_close_button_to_tab(tab_main_frame)
        loading_label = tk.Label(
            content_area,
            text=(f"🔄 {get_string('curve_fitting', 'loading', self.language)}..."),
            font=("Arial", 12),
            fg="gray",
        )
        loading_label.pack(expand=True)
        content_area.update()
        try:
            curve_fitting_instance = AjusteCurvaFrame(content_area, self.language)
            loading_label.destroy()
            curve_fitting_instance.pack(
                fill=tk.BOTH, expand=True
            )
            self.open_tabs[tab_key] = {
                "widget": tab_main_frame,
                "instance": curve_fitting_instance,
                "tab_type": "curve_fitting",
                "created_time": time.time(),
            }
            self.notebook.select(tab_main_frame)
        except Exception as e:  # pylint: disable=broad-except
            loading_label.destroy()
            logging.error("Failed to create curve fitting tab: %s", e)
            show_error(
                get_string("main_app", "error", self.language),
                get_string("curve_fitting", "load_error", self.language),
            )

    def open_uncertainty_calc_tab(self) -> None:
        """Open a new uncertainty calculator tab using the translation API."""
        # pylint: disable=invalid-name
        CalculoIncertezasFrame = lazy_import(
            "app_files.gui.incerteza.calculo_incertezas_gui",
            "CalculoIncertezasFrame",
            preload_priority=3,
            dependencies=["sympy"],
        )
        i = 1
        while f"uncertainty_calc_{i}" in self.open_tabs:
            i += 1
        tab_key = f"uncertainty_calc_{i}"
        tab_main_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            tab_main_frame,
            text=get_string("uncertainty_calc", "tab_title", self.language),
        )
        content_area = self.add_close_button_to_tab(tab_main_frame)
        loading_label = tk.Label(
            content_area,
            text=(f"🔄 {get_string('uncertainty_calc', 'loading', self.language)}..."),
            font=("Arial", 12),
            fg="gray",
        )
        loading_label.pack(expand=True)
        content_area.update()
        try:
            uncertainty_calc_instance = CalculoIncertezasFrame(
                content_area, self.language
            )
            loading_label.destroy()
            # Use grid on the main_frame, not on the logic class instance
            uncertainty_calc_instance.main_frame.grid(row=0, column=0, sticky="nsew")
            self.open_tabs[tab_key] = {
                "widget": tab_main_frame,
                "instance": uncertainty_calc_instance,
                "tab_type": "uncertainty_calc",
                "created_time": time.time(),
            }
            self.notebook.select(tab_main_frame)
        except Exception as e:  # pylint: disable=broad-except
            loading_label.destroy()
            logging.error("Failed to create uncertainty calculator tab: %s", e)
            show_error(
                get_string("main_app", "error", self.language),
                get_string("uncertainty_calc", "load_error", self.language),
            )

    def handle_tab_changed(self) -> None:
        """Handle tab changed event and call on_tab_activated if present."""
        _tab_ids_tuple: tuple[Any, ...] = tuple(self.notebook.tabs())
        if not _tab_ids_tuple:
            return
        try:
            current_tab_path = self.notebook.select()
            if not current_tab_path:
                return
            current_widget = self.notebook.nametowidget(current_tab_path)
            found_instance = None
            for tab_data_entry in self.open_tabs.values():
                if tab_data_entry.get("widget") == current_widget:
                    found_instance = tab_data_entry.get("instance")
                    break
            if found_instance and hasattr(found_instance, "on_tab_activated"):
                found_instance.on_tab_activated()
        except tk.TclError as e:
            logging.error("Error in tab changed: %s", e)

    def update_tab_titles(self) -> None:
        """Update all tab titles using the translation API."""
        tab_ids: list[Any] = list(self.notebook.tabs())
        for i, tab_id in enumerate(tab_ids):
            # Get the tab widget
            tab_widget = self.notebook.nametowidget(tab_id)
            # Check if it's the home tab
            if tab_widget == self.home_tab:
                self.notebook.tab(i, text=get_string("main_app", "home", self.language))
            else:
                # Find the corresponding tab data
                tab_data = None
                for td in self.open_tabs.values():
                    if td.get("widget") == tab_widget:
                        tab_data = td
                        break

                if tab_data:
                    tab_type = tab_data.get("tab_type")
                    if tab_type:
                        self.notebook.tab(
                            i, text=get_string(tab_type, "tab_title", self.language)
                        )

    def switch_language(self, new_language: str) -> None:
        """Switch language for all open tab instances."""
        self.language = new_language
        # Update tab titles first
        self.update_tab_titles()
        # Update language for each open tab instance that supports it
        for tab_data in self.open_tabs.values():
            instance = tab_data.get("instance")
            tab_type = tab_data.get("tab_type")
            # Update ALL tabs that support switch_language
            if instance and hasattr(instance, "switch_language"):
                try:
                    instance.switch_language(new_language)
                    logging.debug(f"Language switched successfully for {tab_type} tab")
                except Exception as e:
                    logging.error(
                        f"Error switching language for tab " f"{tab_type}: {e}",
                        exc_info=True,
                    )
