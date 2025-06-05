"""Launcher script for AnaFis"""
import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app_files'))

from app_files.main import AplicativoUnificado
from app_files.utils.user_preferences import user_preferences
from app_files.utils.constants import TRANSLATIONS

def show_splash_screen():
    """Shows a splash screen with loading progress"""    # Load user preferences first to get the correct language
    current_language = user_preferences.get_preference('language', 'pt')
    
    splash = tk.Tk()
    splash.title(TRANSLATIONS[current_language]['loading_title'])
    splash.geometry("300x100")
    splash.resizable(False, False)
    splash.configure(bg="#f0f0f0")
    
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
    def update_progress(i=0):
        if i <= 100:
            progress['value'] = i
            splash.update_idletasks()
            # Schedule the next update
            splash.after(20, lambda: update_progress(i+1))
        else:
            # When progress is complete, destroy splash and start app
            splash.destroy()
            # Initialize and run app
            app = AplicativoUnificado()
            app.run()
    
    # Start the progress update
    splash.after(100, update_progress)
    
    # Start the Tkinter main loop
    splash.mainloop()

if __name__ == "__main__":
    main()