"""Launcher script for AnaFis"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

# Add app_files to path before importing from it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# pylint: disable=wrong-import-position
from app_files.main import AplicativoUnificado
from app_files.utils.user_preferences import user_preferences
from app_files.utils.constants import TRANSLATIONS

def set_window_icon(window: tk.Tk) -> Optional[tk.PhotoImage]:
    """Set the application icon for any window"""
    try:
        # Get the path to the icon file in the app_files/utils folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, 'app_files', 'utils', 'icon.png')

        # Check if the icon file exists
        if not os.path.exists(icon_path):
            logging.warning("Icon file not found at: %s", icon_path)
            return None

        # Create a PhotoImage from the icon file
        icon = tk.PhotoImage(file=icon_path)

        # Set as window icon
        window.iconphoto(True, icon)

        return icon

    except (OSError, tk.TclError) as e:
        logging.error("Error setting window icon: %s", e)
        return None

def show_splash_screen() -> tuple[tk.Tk, ttk.Progressbar]:
    """Shows a splash screen with loading progress"""
    # Load user preferences first to get the correct language
    current_language = user_preferences.get_preference('language', 'pt')

    splash = tk.Tk()
    splash.title(TRANSLATIONS[current_language]['loading_title'])    
    splash.geometry("300x100")
    splash.resizable(False, False)
    splash.configure(bg="#f0f0f0")
    
    # Set the application icon for the splash screen
    set_window_icon(splash)

    # Center the window
    width = splash.winfo_screenwidth()
    height = splash.winfo_screenheight()
    x = int((width - 300) / 2)
    y = int((height - 100) / 2)    
    splash.geometry(f"300x100+{x}+{y}")
    
    # Add a label
    ttk.Label(
        splash,
        text=TRANSLATIONS[current_language]['loading_message'],
        font=("Segoe UI", 12),
        background="#f0f0f0"
    ).pack(pady=10)

    # Add progress bar
    progress = ttk.Progressbar(
        splash,
        orient="horizontal",
        length=250,
        mode="determinate"
    )
    progress.pack(pady=10)

    return splash, progress

def main():
    """Main entry point for the application"""
    # Show splash screen
    splash, progress = show_splash_screen()
    # Function to update progress
    def update_progress(i: int = 0) -> None:
        if i <= 100:
            progress['value'] = i
            splash.update_idletasks()
            # Schedule the next update
            splash.after(20, lambda: update_progress(i+1))
        else:
            # When progress is complete, destroy splash and start app
            splash.destroy()            # Initialize and run app
            app = AplicativoUnificado()
            app.run()
    
    # Start the progress update
    splash.after(100, update_progress)

    # Start the Tkinter main loop
    splash.mainloop()

if __name__ == "__main__":
    main()
