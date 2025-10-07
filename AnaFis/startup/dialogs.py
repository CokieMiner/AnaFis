# pylint: disable=import-error
"""Splash and error dialog utilities for AnaFis startup."""
import logging
import os
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from typing import Tuple, Any
from startup.appdata import ensure_app_data_directories
from app_files.utils.translations.api import get_string


def set_window_icon(window: tk.Tk) -> None:
    """Set the window icon for the given Tk window."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(
            os.path.dirname(current_dir), "app_files", "utils", "icon.png"
        )
        icon = tk.PhotoImage(file=icon_path, name=f"splash_icon_{id(window)}")
        window.iconphoto(True, icon)
        if not hasattr(window, "_icon_set"):
            window._icon_set = True    # pylint: disable=protected-access  # Justification: Used to prevent duplicate icon setting
    except (OSError, tk.TclError) as e:
        logging.error("Error setting window icon: %s", e)


def show_initialization_screen(
    timing_tracker: Any,
) -> Tuple[tk.Tk, ttk.Progressbar, ttk.Label]:
    """Show the splash screen and return splash, progress, status_label."""
    timing_tracker.mark_splash_start()
    splash = ThemedTk(theme="plastik")
    splash.title("AnaFis")
    splash.geometry("400x150")
    splash.resizable(False, False)
    splash.update_idletasks()
    width = splash.winfo_screenwidth()
    height = splash.winfo_screenheight()
    x = int((width - 400) / 2)
    y = int((height - 150) / 2)
    splash.geometry(f"400x150+{x}+{y}")
    main_frame = ttk.Frame(splash)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    title_label = ttk.Label(main_frame, text="AnaFis", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 10))
    status_label = ttk.Label(main_frame, text="Initializing...", font=("Segoe UI", 10))
    status_label.pack(pady=(0, 10))
    progress = ttk.Progressbar(
        main_frame, orient="horizontal", length=350, mode="determinate"
    )
    progress.pack(pady=(0, 10))
    splash.update()

    def initialize_splash_after_show():
        try:
            from app_files.utils.user_preferences import user_preferences    # pylint: disable=import-outside-toplevel

            # Justification: Lazy import to avoid circular dependencies
            current_language = user_preferences.get_preference("language", "pt")
            splash.title(
                get_string("main_app", "loading_title", current_language, "AnaFis")
            )
            status_label.config(
                text=get_string(
                    "main_app", "initializing", current_language, "Initializing..."
                )
            )
            set_window_icon(splash)
            ensure_app_data_directories()
            splash.update()
        except (
            Exception
        ) as e:  # pylint: disable=broad-exception-caught  # Justification: Splash must not crash
            logging.error("Error in post-splash initialization: %s", e)

    splash.after(1, initialize_splash_after_show)
    return splash, progress, status_label


def show_error_and_exit(error_msg: str) -> None:
    """Show error message and exit."""
    error_window = ThemedTk(theme="plastik")
    try:
        from app_files.utils.user_preferences import user_preferences    # pylint: disable=import-outside-toplevel

        # Justification: Lazy import to avoid circular dependencies
        current_language = user_preferences.get_preference("language", "pt")
        error_window.title(
            get_string(
                "main_app",
                "initialization_error_title",
                current_language,
                "Initialization Error",
            )
        )
        error_text = get_string(
            "main_app",
            "anafis_initialization_error",
            current_language,
            "AnaFis Initialization Error",
        )
        failed_message = get_string(
            "main_app",
            "initialization_failed_message",
            current_language,
            "Application initialization failed",
        )
        exit_text = get_string("main_app", "exit_application", current_language, "Exit")
    except (
        Exception
    ):  # pylint: disable=broad-exception-caught  # Justification: Fallback to English if translation fails
        error_window.title("Initialization Error")
        error_text = "AnaFis Initialization Error"
        failed_message = "Application initialization failed"
        exit_text = "Exit"
    error_window.geometry("500x300")
    error_window.resizable(False, False)
    error_window.update_idletasks()
    width = error_window.winfo_screenwidth()
    height = error_window.winfo_screenheight()
    x = int((width - 500) / 2)
    y = int((height - 300) / 2)
    error_window.geometry(f"500x300+{x}+{y}")
    frame = ttk.Frame(error_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    error_color = "red"
    ttk.Label(
        frame, text=error_text, font=("Segoe UI", 14, "bold"), foreground=error_color
    ).pack(pady=(0, 15))
    ttk.Label(frame, text=failed_message, font=("Segoe UI", 10)).pack(pady=(0, 10))
    text_frame = ttk.Frame(frame)
    text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    text_widget = tk.Text(text_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
    scrollbar = ttk.Scrollbar(
        text_frame, orient="vertical", command=text_widget.yview
    )
    text_widget.configure(yscrollcommand=scrollbar.set)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.insert("1.0", error_msg)
    text_widget.config(state=tk.DISABLED)
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X)

    def close_app():
        import sys  # pylint: disable=import-outside-toplevel  # Justification: Close app on button click

        error_window.destroy()
        sys.exit(1)

    ttk.Button(button_frame, text=exit_text, command=close_app).pack(pady=(0, 0))
    error_window.attributes("-topmost", True)
    error_window.focus_force()
    error_window.mainloop()
