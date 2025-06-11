"""Launcher script for AnaFis with advanced initialization"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import logging
import threading
from typing import Optional, List, Callable, Any

# Add app_files to path before importing from it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only what's needed for the splash screen initially
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

class InitializationManager:
    """Manages the initialization process with progress tracking"""
    
    def __init__(self, language: str):
        self.language = language
        self.tasks: List[tuple[str, Callable[[], Any]]] = []
        self.current_task = 0
        self.total_tasks = 0
        
    def add_task(self, name: str, func: Callable[[], Any]) -> None:
        """Add an initialization task"""
        self.tasks.append((name, func))
        self.total_tasks = len(self.tasks)
    
    def execute_tasks(self, progress_callback: Callable[[int, str], None]) -> None:
        """Execute all initialization tasks with progress updates"""
        for i, (task_name, task_func) in enumerate(self.tasks):
            try:
                progress_callback(int((i / self.total_tasks) * 100), task_name)
                task_func()
                # No artificial delay - let real work determine timing
            except Exception as e:
                logging.error(f"Error in initialization task '{task_name}': {e}")
                
        # Complete
        progress_callback(100, TRANSLATIONS[self.language]['initialization_complete'])

def initialize_modules() -> None:
    """Initialize application modules with real imports"""
    try:
        # Import essential scientific computing modules
        import numpy
        import scipy
        import matplotlib
        matplotlib.use('TkAgg')  # Set backend for tkinter
        
        # Import GUI modules to ensure they're loaded
        from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
        from app_files.gui.incerteza.calculo_incertezas_gui import CalculoIncertezasFrame
        from app_files.gui.settings.settings_dialog import SettingsDialog
        
        # Store references to prevent garbage collection
        _loaded_modules: List[Any] = [AjusteCurvaFrame, CalculoIncertezasFrame, SettingsDialog]
        
        logging.info(f"Modules loaded: numpy {numpy.__version__}, scipy {scipy.__version__}")
        logging.info(f"GUI components loaded: {len(_loaded_modules)} modules")
        
    except ImportError as e:
        logging.warning(f"Optional module not available: {e}")
    except Exception as e:
        logging.error(f"Error initializing modules: {e}")

def load_plugins() -> None:
    """Load and initialize plugins"""
    try:
        from app_files.utils.plugin_system import plugin_manager
        plugin_manager.discover_plugins()
        plugin_manager.load_plugins()
    except ImportError:
        logging.warning("Plugin system not available")
    except Exception as e:
        logging.error(f"Error loading plugins: {e}")

def show_initialization_screen() -> tuple[tk.Tk, ttk.Progressbar, ttk.Label]:
    """Shows an initialization screen with detailed progress"""
    # Load user preferences first to get the correct language
    current_language = user_preferences.get_preference('language', 'pt')

    splash = tk.Tk()
    splash.title(TRANSLATIONS[current_language]['loading_title'])    
    splash.geometry("400x150")
    splash.resizable(False, False)
    splash.configure(bg="#f0f0f0")
    
    # Set the application icon for the splash screen
    set_window_icon(splash)

    # Center the window
    width = splash.winfo_screenwidth()
    height = splash.winfo_screenheight()
    x = int((width - 400) / 2)
    y = int((height - 150) / 2)    
    splash.geometry(f"400x150+{x}+{y}")
    
    # Main frame
    main_frame = ttk.Frame(splash)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title label
    title_label = ttk.Label(
        main_frame,
        text="AnaFis",
        font=("Segoe UI", 16, "bold")
    )
    title_label.pack(pady=(0, 10))
    
    # Status label
    status_label = ttk.Label(
        main_frame,
        text=TRANSLATIONS[current_language]['initializing'],
        font=("Segoe UI", 10)
    )
    status_label.pack(pady=(0, 10))

    # Progress bar
    progress = ttk.Progressbar(
        main_frame,
        orient="horizontal",
        length=350,
        mode="determinate"
    )
    progress.pack(pady=(0, 10))
    
    # Version label
    from app_files import __version__
    version_label = ttk.Label(
        main_frame,
        text=f"v{__version__}",
        font=("Segoe UI", 8),
        foreground="#666666"
    )
    version_label.pack()

    return splash, progress, status_label

def main():
    """Main entry point for the application"""
    # Load user preferences first to get the correct language
    current_language = user_preferences.get_preference('language', 'pt')
    
    # Show initialization screen
    splash, progress, status_label = show_initialization_screen()
    
    # Create initialization manager
    init_manager = InitializationManager(current_language)
    
    # Add initialization tasks
    init_manager.add_task(
        TRANSLATIONS[current_language].get('loading_preferences', 'Loading preferences...'),
        lambda: logging.info("User preferences loaded")
    )
    
    init_manager.add_task(
        TRANSLATIONS[current_language].get('loading_features', 'Initializing features...'),
        lambda: logging.info("Features initialized")
    )
    
    init_manager.add_task(
        TRANSLATIONS[current_language].get('loading_modules', 'Loading modules...'),
        initialize_modules
    )
    
    init_manager.add_task(
        TRANSLATIONS[current_language].get('loading_plugins', 'Loading plugins...'),
        load_plugins
    )
    
    init_manager.add_task(
        TRANSLATIONS[current_language].get('loading_interface', 'Loading interface...'),
        lambda: logging.info("Interface ready")
    )
    
    def update_progress(progress_val: int, task_name: str) -> None:
        """Update progress bar and status"""
        progress['value'] = progress_val
        status_label.config(text=task_name)
        splash.update_idletasks()
    
    def run_initialization() -> None:
        """Run initialization in separate thread"""
        try:
            init_manager.execute_tasks(update_progress)
            
            # When initialization is complete, switch to main app
            splash.after(500, start_main_app)
            
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            splash.after(0, lambda: show_error_and_exit(str(e)))
    
    def start_main_app() -> None:
        """Start the main application"""
        try:
            splash.destroy()
            
            # Import and start main app
            from app_files.main import AplicativoUnificado
            app = AplicativoUnificado()
            app.run()
            
        except Exception as e:
            logging.error(f"Failed to start main application: {e}")
            show_error_and_exit(str(e))
    
    def show_error_and_exit(error_msg: str) -> None:
        """Show error message and exit"""
        try:
            splash.destroy()
        except Exception:
            pass
            
        error_window = tk.Tk()
        error_window.title("Initialization Error")
        error_window.geometry("500x300")
        error_window.configure(bg="#f0f0f0")
        error_window.resizable(False, False)
        
        # Center error window
        error_window.update_idletasks()
        width = error_window.winfo_screenwidth()
        height = error_window.winfo_screenheight()
        x = int((width - 500) / 2)
        y = int((height - 300) / 2)
        error_window.geometry(f"500x300+{x}+{y}")
        
        frame = ttk.Frame(error_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            frame,
            text="AnaFis Initialization Error",
            font=("Segoe UI", 14, "bold"),
            foreground="red"
        ).pack(pady=(0, 15))
        
        ttk.Label(
            frame,
            text="The application failed to initialize properly:",
            font=("Segoe UI", 10)
        ).pack(pady=(0, 10))
        
        # Error message in scrollable text widget
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_widget = tk.Text(text_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)  # type: ignore
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert("1.0", error_msg)
        text_widget.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        def close_app():
            error_window.destroy()
            sys.exit(1)
        
        ttk.Button(
            button_frame,
            text="Exit Application",
            command=close_app
        ).pack(pady=(0, 0))
        
        # Make sure the error window stays on top
        error_window.attributes('-topmost', True)  # type: ignore
        error_window.focus_force()
        
        error_window.mainloop()
    
    # Start initialization in background thread
    init_thread = threading.Thread(target=run_initialization, daemon=True)
    init_thread.start()
    
    # Start the splash screen main loop
    splash.mainloop()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    main()
