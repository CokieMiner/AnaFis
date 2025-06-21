"""Launcher script for AnaFis with advanced initialization"""
import time
startup_start_time = time.time()
import sys
import os
import signal
import tkinter as tk
from tkinter import ttk
import logging
import threading
from typing import Optional, List, Callable, Any

# Global timing variables
splash_start_time: Optional[float] = None
splash_end_time: Optional[float] = None
app_ready_time: Optional[float] = None

# Add app_files to path before importing from it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Minimal imports needed for splash screen
# Import only what's needed for the splash screen initially - defer the rest
from app_files.utils.constants import TRANSLATIONS

# Defer user_preferences import - we'll load it right before showing splash
# This avoids file I/O operations before the splash screen appears

def handle_signal(signum: int, frame: Any) -> None:
    """Handle termination signals"""
    logging.info(f"Received signal {signum}, terminating application...")
    # Force exit without cleanup to avoid hanging
    os._exit(0)

def setup_signal_handlers() -> None:
    """Setup signal handlers for proper application termination"""
    try:
        signal.signal(signal.SIGINT, handle_signal)  # Ctrl+C
        signal.signal(signal.SIGTERM, handle_signal)  # Termination signal
        if hasattr(signal, 'SIGBREAK'):  # Windows specific
            signal.signal(signal.SIGBREAK, handle_signal)
    except Exception as e:
        logging.debug(f"Could not setup signal handlers: {e}")

# Apply startup optimizations in background thread after splash is visible
def apply_startup_optimizations():
    """Apply various optimizations to improve application startup time"""
    try:
        from build_scripts.optimize_startup import optimize_imports
        optimize_imports()
    except ImportError:
        # Fallback optimization if build_scripts not available
        import gc
        gc.disable()  # Disable GC during startup
        threading.Timer(3.0, gc.enable).start()  # Re-enable after 3 seconds

def set_window_icon(window: tk.Tk) -> Optional[tk.PhotoImage]:
    """Set the application icon for any window"""
    try:
        # Get the path to the icon file in the app_files/utils folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, 'app_files', 'utils', 'icon.png')

        # Don't check if file exists to save an I/O operation during startup
        # Just handle exceptions if the file is missing
        icon = tk.PhotoImage(file=icon_path, name=f"splash_icon_{id(window)}")
        window.iconphoto(True, icon)  # Use False to only set for this window, not all future windows
        
        # Mark that icon has been set to prevent conflicts
        window._icon_set = True  # type: ignore
        
        return icon

    except (OSError, tk.TclError) as e:
        logging.error("Error setting window icon: %s", e)
        return None

def log_timing_info() -> None:
    """Log detailed timing information about the application startup"""
    global startup_start_time, splash_start_time, splash_end_time, app_ready_time
    
    if splash_start_time and splash_end_time:
        splash_duration = splash_end_time - splash_start_time
        logging.info(f"Splash screen displayed for: {splash_duration:.3f} seconds")
    
    if app_ready_time:
        total_startup_time = app_ready_time - startup_start_time
        logging.info(f"Total application startup time: {total_startup_time:.3f} seconds")
        
        if splash_end_time:
            post_splash_time = app_ready_time - splash_end_time
            logging.info(f"Post-splash initialization time: {post_splash_time:.3f} seconds")
    
    # Also print to console for visibility
    if splash_start_time and splash_end_time and app_ready_time:
        splash_duration = splash_end_time - splash_start_time
        total_time = app_ready_time - startup_start_time
        print(f"\n=== AnaFis Startup Timing ===")
        print(f"Splash screen duration: {splash_duration:.3f}s")
        print(f"Total startup time: {total_time:.3f}s")
        print(f"================================\n")

def mark_splash_start() -> None:
    """Mark the start time of the splash screen"""
    global splash_start_time
    splash_start_time = time.time()
    logging.debug("Splash screen start time recorded")

def mark_splash_end() -> None:
    """Mark the end time of the splash screen"""
    global splash_end_time
    splash_end_time = time.time()
    logging.debug("Splash screen end time recorded")

def mark_app_ready() -> None:
    """Mark when the application is fully ready"""
    global app_ready_time
    app_ready_time = time.time()
    logging.debug("Application ready time recorded")
    # Log timing info when app is ready
    log_timing_info()
    # Track detailed startup metrics
    track_startup_metrics()

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
        import numpy  # type: ignore
        import scipy  # type: ignore
        import matplotlib  # type: ignore
        matplotlib.use('TkAgg')  # Set backend for tkinter
        
        # Configure matplotlib to prevent icon conflicts and warnings
        import matplotlib as mpl  # type: ignore
        mpl.rcParams['figure.max_open_warning'] = 50  # Increase warning threshold
        mpl.rcParams['tk.window_focus'] = False  # Prevent matplotlib windows from stealing focus
        
        # Import GUI modules to ensure they're loaded
        from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
        from app_files.gui.incerteza.calculo_incertezas_gui import CalculoIncertezasFrame
        from app_files.gui.settings.settings_dialog import SettingsDialog
        
        # Store references to prevent garbage collection
        _loaded_modules: List[Any] = [AjusteCurvaFrame, CalculoIncertezasFrame, SettingsDialog]
        
        logging.info(f"Modules loaded: numpy {numpy.__version__}, scipy {scipy.__version__}")  # type: ignore
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

def ensure_theme_directories() -> None:
    """
    Ensure custom theme directories exist without loading the full theme manager
    """
    try:
        # Get app data directory (simplified version)
        if os.name == 'nt':
            appdata_local = os.environ.get('LOCALAPPDATA')
            if appdata_local:
                app_data_dir = os.path.join(appdata_local, 'AnaFis')
            else:
                app_data_dir = os.path.expanduser('~\\AppData\\Local\\AnaFis')
        else:
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                app_data_dir = os.path.join(xdg_config, 'anafis')
            else:
                app_data_dir = os.path.expanduser('~/.config/anafis')
        
        # Create application data directory
        os.makedirs(app_data_dir, exist_ok=True)
        logging.info("Application data directory verified/created")
    except Exception as e:
        logging.warning(f"Could not create application data directories: {e}")

def show_initialization_screen() -> tuple[tk.Tk, ttk.Progressbar, ttk.Label]:
    """Shows an initialization screen with minimal delay"""
    
    # Mark splash screen start time
    mark_splash_start()
    
    # Create splash window FIRST - no imports or I/O operations before this
    splash = tk.Tk()
    splash.title("AnaFis")  # Use hardcoded title initially
    splash.geometry("400x150")
    splash.resizable(False, False)
    
    # Center the window immediately
    splash.update_idletasks()
    width = splash.winfo_screenwidth()
    height = splash.winfo_screenheight()
    x = int((width - 400) / 2)
    y = int((height - 150) / 2)    
    splash.geometry(f"400x150+{x}+{y}")
    
    # Create basic UI elements with minimal styling
    main_frame = ttk.Frame(splash)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title label
    title_label = ttk.Label(
        main_frame,
        text="AnaFis",
        font=("Segoe UI", 16, "bold")
    )
    title_label.pack(pady=(0, 10))
    
    # Status label - start with generic message
    status_label = ttk.Label(
        main_frame,
        text="Initializing...",
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
    
    # Force the splash screen to show immediately
    splash.update()
    
    # Now do all the expensive operations AFTER the window is visible
    def initialize_splash_after_show():
        try:
            # Import user_preferences now
            from app_files.utils.user_preferences import user_preferences
            
            # Load preferences
            current_language = user_preferences.get_preference('language', 'pt')
            # Skip theme loading for faster startup - themes will be loaded on-demand
            
            # Update title with correct language
            splash.title(TRANSLATIONS[current_language]['loading_title'])
            
            # Update status label with correct language
            status_label.config(text=TRANSLATIONS[current_language]['initializing'])
            
            # Skip theme application to splash screen for faster startup
            # actual_theme = apply_splash_theme(splash, current_theme)
            # logging.debug(f"Splash screen theme applied: {actual_theme}")
            
            # Set icon
            set_window_icon(splash)
            
            # Create directories in background
            ensure_theme_directories()
            
            splash.update()
            
        except Exception as e:
            logging.error(f"Error in post-splash initialization: {e}")
    
    # Schedule the expensive operations to run after the window is shown
    splash.after(1, initialize_splash_after_show)
    
    return splash, progress, status_label

def main():
    """Main entry point for the application"""
    # Setup signal handlers for proper termination
    setup_signal_handlers()
    
    # Show splash screen immediately with zero imports
    splash, progress, status_label = show_initialization_screen()
    
    def setup_initialization():
        """Setup initialization after splash is visible"""
        try:
            # Now import and setup everything else
            from app_files.utils.user_preferences import user_preferences
            
            # Start optimization in background
            threading.Thread(target=apply_startup_optimizations, daemon=True).start()
            
            # Load user preferences to get the correct language
            current_language = user_preferences.get_preference('language', 'pt')
            
            # Create initialization manager
            init_manager = InitializationManager(current_language)
            
            # Add initialization tasks
            init_manager.add_task(
                TRANSLATIONS[current_language].get('loading_preferences', 'Loading preferences...'),
                lambda: logging.info("User preferences loaded")
            )
            
            # Skip theme loading during startup for faster boot
            # Themes will be loaded on-demand when first accessed
            
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
            
            # Theme manager is now initialized inside the main app
            # init_manager.add_task(
            #     TRANSLATIONS[current_language].get('loading_themes', 'Loading themes...'),
            #     load_theme_manager
            # )
            
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
                    # Create a proper progress callback function to avoid lambda issues
                    def progress_callback(val: int, msg: str) -> None:
                        try:
                            update_progress(int(val * 0.8), msg)
                        except Exception as e:
                            logging.error(f"Error in progress callback: {e}")
                    
                    # Phase 1: Basic initialization (non-GUI tasks)
                    init_manager.execute_tasks(progress_callback)
                    
                    # Phase 2: Main app loading (must run on main GUI thread)
                    splash.after(0, start_main_app)
                    
                except Exception as e:
                    logging.error(f"Initialization failed: {e}")
                    def show_error():
                        try:
                            show_error_and_exit(str(e))
                        except Exception as error_e:
                            logging.error(f"Error showing error dialog: {error_e}")
                    splash.after(0, show_error)
            
            def start_main_app() -> None:
                """Start the main application"""
                try:
                    # Update splash to show final loading phase (80%)
                    update_progress(80, "Loading main application...")
                    
                    # Import main app class
                    from app_files.main import AplicativoUnificado
                    
                    # Update splash for app initialization (82%)
                    update_progress(82, "Initializing application...")
                    
                    # Create the main app instance (UI only, no heavy loading yet)
                    # Pass splash window to avoid creating multiple windows
                    splash.withdraw()  # Hide splash temporarily
                    app = AplicativoUnificado(root=splash)
                    
                    # Theme manager is now initialized inside app.initialize_utilities
                    
                    # Now run heavy utility initialization with continuous progress updates (82-100%)
                    def splash_progress(val: int, msg: str) -> None:
                        # Map 91-100% from utilities to 82-100% on main progress bar
                        mapped_val = 82 + ((val - 91) / 9) * 18  # Map 91-100 to 82-100
                        splash.deiconify()  # Re-show splash during loading
                        update_progress(int(mapped_val), msg)
                    
                    app.initialize_utilities(progress_callback=splash_progress)
                    
                    # Update splash one final time (100%)
                    update_progress(100, "Application ready!")                    # Small delay to show completion, then convert splash to main app
                    def finalize_startup():
                        try:
                            # Mark splash screen end before destroying it
                            mark_splash_end()
                              # Create a smooth transition by overlaying the main UI
                            # Hide the splash widgets first
                            splash_widgets: List[tk.Widget] = []
                            for child in splash.winfo_children():
                                splash_widgets.append(child)
                                child.pack_forget()
                                child.grid_forget()
                                child.place_forget()
                            
                            # Immediately setup the main UI to prevent white flash
                            try:
                                app.setup_ui()
                                
                                # Force update to render the main UI
                                splash.update_idletasks()
                                
                                # Now destroy the splash widgets
                                for widget in splash_widgets:
                                    try:
                                        widget.destroy()
                                    except tk.TclError:
                                        pass
                                        
                                # Mark app as fully ready
                                mark_app_ready()
                                
                                # Run the main app
                                app.run()
                                
                            except tk.TclError as ui_error:
                                # If there's a geometry manager conflict, try a different approach
                                logging.warning(f"UI setup conflict: {ui_error}")
                                
                                # Destroy splash widgets first
                                for widget in splash_widgets:
                                    try:
                                        widget.destroy()
                                    except tk.TclError:
                                        pass
                                
                                # Force window to update
                                splash.update()
                                
                                # Try setting up UI again
                                app.setup_ui()
                                mark_app_ready()
                                app.run()
                                
                        except Exception as e:
                            logging.error(f"Error during final startup: {e}")
                            show_error_and_exit(str(e))
                    
                    splash.after(500, finalize_startup)
                    
                except Exception as e:
                    logging.error(f"Failed to start main application: {e}")
                    show_error_and_exit(str(e))

            # Start initialization in background thread
            init_thread = threading.Thread(target=run_initialization, daemon=True)
            init_thread.start()
            
        except Exception as e:
            logging.error(f"Setup initialization failed: {e}")
            show_error_and_exit(str(e))
    
    # Schedule setup to run after splash is shown
    splash.after(10, setup_initialization)
    
    # Start the splash screen main loop
    splash.mainloop()

def show_error_and_exit(error_msg: str) -> None:
    """Show error message and exit"""
    error_window = tk.Tk()
    
    try:
        # Import here to avoid early loading
        from app_files.utils.user_preferences import user_preferences
        # Load user preferences to get the correct language
        current_language = user_preferences.get_preference('language', 'pt')
        
        error_window.title(TRANSLATIONS[current_language]['initialization_error_title'])
        error_text = TRANSLATIONS[current_language]['anafis_initialization_error']
        failed_message = TRANSLATIONS[current_language]['initialization_failed_message']
        exit_text = TRANSLATIONS[current_language]['exit_application']
    except Exception:
        # Fallback if preferences fail
        error_window.title("Initialization Error")
        error_text = "AnaFis Initialization Error"
        failed_message = "Application initialization failed"
        exit_text = "Exit"
    
    error_window.geometry("500x300")
    
    # Use theme-appropriate background color for error window
    try:
        from app_files.utils.theme_manager import theme_manager
        if theme_manager.is_initialized:
            bg_color = theme_manager.get_adaptive_color('background')
            error_window.configure(bg=bg_color)
        else: 
            error_window.configure(bg="#f0f0f0")  # Fallback
    except ImportError:
        error_window.configure(bg="#f0f0f0")  # Fallback
    
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
    
    # Use theme-appropriate error color for error message
    try:
        from app_files.utils.theme_manager import theme_manager
        if theme_manager.is_initialized:
            error_color = theme_manager.get_adaptive_color('text_error')
        else:
            error_color = "red"  # Fallback if theme manager not ready
    except ImportError:
        error_color = "red"  # Fallback if theme manager unavailable
    
    ttk.Label(
        frame,
        text=error_text,
        font=("Segoe UI", 14, "bold"),
        foreground=error_color
    ).pack(pady=(0, 15))
    
    ttk.Label(
        frame,
        text=failed_message,
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
        text=exit_text,
        command=close_app
    ).pack(pady=(0, 0))
    
    # Make sure the error window stays on top
    error_window.attributes('-topmost', True)  # type: ignore
    error_window.focus_force()
    
    error_window.mainloop()

def track_startup_metrics():
    """Track and log startup performance metrics"""
    import json
    from pathlib import Path
    
    try:
        # Calculate timing metrics
        total_startup_time = time.time() - startup_start_time
        splash_duration = (splash_end_time - splash_start_time) if splash_start_time and splash_end_time else 0
        app_init_time = (app_ready_time - splash_end_time) if splash_end_time and app_ready_time else 0
        
        # Create metrics data
        metrics = {  # type: ignore[misc]
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_startup_time': round(total_startup_time, 3),
            'splash_duration': round(splash_duration, 3),
            'app_initialization_time': round(app_init_time, 3),
            'python_version': sys.version.split()[0],
            'platform': os.name
        }
        
        # Log the metrics
        logging.info(f"Startup metrics: Total={metrics['total_startup_time']}s, "
                    f"Splash={metrics['splash_duration']}s, "
                    f"Init={metrics['app_initialization_time']}s")
        
        # Optionally save to file for historical tracking
        try:
            # Get user's temp directory for metrics storage
            if os.name == 'nt':
                metrics_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / 'AnaFis' / 'metrics'
            else:
                metrics_dir = Path.home() / '.config' / 'anafis' / 'metrics'
            
            metrics_dir.mkdir(parents=True, exist_ok=True)
            metrics_file = metrics_dir / 'startup_metrics.jsonl'
            
            # Append metrics to file (JSONL format for easy parsing)
            with open(metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics) + '\n')
                
            # Keep only last 100 entries to prevent file growth
            if metrics_file.exists():
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if len(lines) > 100:
                    with open(metrics_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines[-100:])
                        
        except (OSError, PermissionError) as e:
            # Don't fail startup if metrics saving fails
            logging.debug(f"Could not save startup metrics: {e}")
            
    except Exception as e:
        # Don't let metrics tracking break the application
        logging.debug(f"Error tracking startup metrics: {e}")

def get_startup_metrics_history(limit: int = 10) -> List[dict]:  # type: ignore[misc]
    """Get recent startup metrics for analysis
    
    Args:
        limit: Maximum number of recent entries to return
        
    Returns:
        List of startup metrics dictionaries
    """
    import json
    from pathlib import Path
    
    try:
        # Get metrics file path
        if os.name == 'nt':
            metrics_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / 'AnaFis' / 'metrics'
        else:
            metrics_dir = Path.home() / '.config' / 'anafis' / 'metrics'
        
        metrics_file = metrics_dir / 'startup_metrics.jsonl'
        
        if not metrics_file.exists():
            return []  # type: ignore[misc]
        
        # Read last 'limit' entries
        with open(metrics_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        metrics_list = []  # type: ignore[misc]
        
        for line in recent_lines:
            try:
                metrics_list.append(json.loads(line.strip()))  # type: ignore[misc]
            except json.JSONDecodeError:
                continue
                
        return metrics_list  # type: ignore[misc]
        
    except Exception as e:
        logging.debug(f"Error reading startup metrics: {e}")
        return []  # type: ignore[misc]

def analyze_startup_performance() -> dict:  # type: ignore[misc]
    """Analyze startup performance trends
    
    Returns:
        Dictionary with performance analysis
    """
    metrics_history = get_startup_metrics_history(50)  # Last 50 startups  # type: ignore[misc]
    
    if not metrics_history:
        return {'status': 'no_data', 'message': 'No startup metrics available'}  # type: ignore[misc]
    
    # Calculate averages and trends
    total_times = [m['total_startup_time'] for m in metrics_history if 'total_startup_time' in m]  # type: ignore[misc]
    splash_times = [m['splash_duration'] for m in metrics_history if 'splash_duration' in m]  # type: ignore[misc]
    init_times = [m['app_initialization_time'] for m in metrics_history if 'app_initialization_time' in m]  # type: ignore[misc]
    
    analysis = {  # type: ignore[misc]
        'status': 'success',
        'sample_size': len(metrics_history),  # type: ignore[misc]
        'average_startup_time': round(sum(total_times) / len(total_times), 3) if total_times else 0,  # type: ignore[misc]
        'average_splash_time': round(sum(splash_times) / len(splash_times), 3) if splash_times else 0,  # type: ignore[misc]
        'average_init_time': round(sum(init_times) / len(init_times), 3) if init_times else 0,  # type: ignore[misc]
        'latest_startup_time': total_times[-1] if total_times else 0,  # type: ignore[misc]
        'fastest_startup': min(total_times) if total_times else 0,  # type: ignore[misc]
        'slowest_startup': max(total_times) if total_times else 0  # type: ignore[misc]
    }
    
    # Calculate trend (last 10 vs previous 10)
    if len(total_times) >= 20:  # type: ignore[misc]
        recent_avg = sum(total_times[-10:]) / 10  # type: ignore[misc]
        previous_avg = sum(total_times[-20:-10]) / 10  # type: ignore[misc]
        trend = round(((recent_avg - previous_avg) / previous_avg) * 100, 1)
        analysis['performance_trend'] = f"{'+' if trend > 0 else ''}{trend}%"
    else:
        analysis['performance_trend'] = 'insufficient_data'
    
    return analysis  # type: ignore[misc]

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    main()
