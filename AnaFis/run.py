"""
This script serves as the main entry point for the AnaFis application.
It handles the startup process, including showing a splash screen, initializing
the application, loading user preferences, and managing the main application
lifecycle.
"""

# pylint: disable=broad-exception-caught
# Reason: Robust startup and error dialogs require catching all exceptions to avoid crashing
# the GUI and to provide user feedback.

import os
import logging
import sys
import threading
from ttkthemes import ThemedTk
from app_files.utils.translations.api import get_string

from startup.timing import timing_tracker
from startup.signals import setup_signal_handlers, apply_startup_optimizations
from startup.dialogs import show_initialization_screen, show_error_and_exit
from startup.init_manager import InitializationManager
from startup.modules import initialize_modules, load_plugins
from startup.startup_optimizer import setup_environment_variables, optimize_memory


# Add app_files to path before importing from it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    """Main entry point for the application"""
    # Apply startup optimizations before anything else
    setup_environment_variables()
    optimize_memory()

    # Setup signal handlers for proper termination
    setup_signal_handlers()

    # Show splash screen immediately with zero imports
    # We'll use Portuguese as the default for the splash until user preference is loaded
    splash, progress, status_label = show_initialization_screen(timing_tracker)

    def setup_initialization() -> None:
        """Setup initialization after splash is visible"""
        try:
            # Now import and setup everything else
            # pylint: disable=import-outside-toplevel
            # Justification: Lazy imports for startup performance
            from app_files.utils.user_preferences import user_preferences
            from app_files.utils.translations.api import log_translation_validation

            # Validate translations early
            log_translation_validation()

            # Start optimization in background
            threading.Thread(target=apply_startup_optimizations, daemon=True).start()

            # Load user preferences to get the correct language
            current_language = user_preferences.get_preference("language", "pt")

            # Create initialization manager
            init_manager = InitializationManager(current_language)

            # Add initialization tasks using the translation API
            init_manager.add_task(
                get_string(
                    "main_app",
                    "loading_preferences",
                    current_language,
                    "Loading preferences...",
                ),
                lambda: logging.info("User preferences loaded"),
            )

            # Skip theme loading during startup for faster boot
            # Themes will be loaded on-demand when first accessed

            init_manager.add_task(
                get_string(
                    "main_app",
                    "loading_features",
                    current_language,
                    "Initializing features...",
                ),
                lambda: logging.info("Features initialized"),
            )

            init_manager.add_task(
                get_string(
                    "main_app",
                    "loading_modules",
                    current_language,
                    "Loading modules...",
                ),
                initialize_modules,
            )

            init_manager.add_task(
                get_string(
                    "main_app",
                    "loading_plugins",
                    current_language,
                    "Loading plugins...",
                ),
                load_plugins,
            )

            init_manager.add_task(
                get_string(
                    "main_app",
                    "loading_interface",
                    current_language,
                    "Loading interface...",
                ),
                lambda: logging.info("Interface ready"),
            )

            def update_progress(progress_val: int, task_name: str) -> None:
                """Update progress bar and status"""
                progress["value"] = progress_val
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
                            logging.error("Error in progress callback: %s", e)

                    # Phase 1: Basic initialization (non-GUI tasks)
                    init_manager.execute_tasks(progress_callback)

                    # Phase 2: Main app loading (must run on main GUI thread)
                    splash.after(0, start_main_app)

                except Exception as e:
                    logging.error("Initialization failed: %s", e)

                    def show_error() -> None:
                        try:
                            show_error_and_exit(str(e))
                        except Exception as error_e:
                            logging.error("Error showing error dialog: %s", error_e)

                    splash.after(0, show_error)

            def start_main_app() -> None:
                """Start the main application"""
                try:
                    # Update splash to show final loading phase (80%)
                    update_progress(
                        80,
                        get_string(
                            "main_app",
                            "loading_main_app",
                            current_language,
                            "Loading main application...",
                        ),
                    )

                    # Update splash for app initialization (82%)
                    update_progress(
                        82,
                        get_string(
                            "main_app",
                            "initializing_app",
                            current_language,
                            "Initializing application...",
                        ),
                    )

                    # Run heavy utility initialization with continuous progress updates (82-100%)
                    def splash_progress(val: int, msg: str) -> None:
                        # Directly map 82-100% for utilities phase
                        try:
                            update_progress(val, msg)
                        except Exception:
                            pass  # Ignore updates after splash is destroyed

                    from app_files.main import (
                        AplicativoUnificado,
                    )  # pylint: disable=import-outside-toplevel

                    # Justification: Lazy import to avoid circular dependencies and speed up splash
                    def finalize_startup() -> None:
                        try:
                            # Mark splash screen end before destroying it
                            timing_tracker.mark_splash_end()

                            # Disable update_progress to prevent further updates
                            nonlocal update_progress

                            def _disabled_update_progress(
                                *args: object, **kwargs: object
                            ) -> None:  # pylint: disable=unused-argument
                                """
                                Required for callback signature, intentionally unused.
                                """

                            update_progress = _disabled_update_progress

                            # Destroy the splash window FIRST
                            splash.destroy()

                            # Load theme from user preferences before creating window
                            from app_files.utils.user_preferences import (
                                user_preferences,
                            )  # pylint: disable=import-outside-toplevel

                            preferred_theme = user_preferences.get_preference(
                                "theme", "plastik"
                            )

                            # Create the main window with the preferred theme (or plastik as default)
                            main_root = ThemedTk(theme=preferred_theme)
                            app = AplicativoUnificado(root=main_root)

                            # Initialize utilities with progress (no theme manager, just plastik)
                            app.initialize_utilities(progress_callback=splash_progress)

                            # Mark app as fully ready
                            timing_tracker.mark_app_ready()

                            # Setup the main UI
                            app.setup_ui()

                            # Run the main app
                            app.run()

                        except Exception as e:
                            logging.error("Error during final startup: %s", e)
                            show_error_and_exit(str(e))

                    splash.after(500, finalize_startup)

                except Exception as e:
                    logging.error("Failed to start main application: %s", e)
                    show_error_and_exit(str(e))

            # Start initialization in background thread
            init_thread = threading.Thread(target=run_initialization, daemon=True)
            init_thread.start()

        except Exception as e:
            logging.error("Setup initialization failed: %s", e)
            show_error_and_exit(str(e))

    # Schedule setup to run after splash is shown
    splash.after(10, setup_initialization)

    # Start the splash screen main loop
    splash.mainloop()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    main()
