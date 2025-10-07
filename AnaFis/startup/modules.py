"""Module and plugin loading utilities for AnaFis startup."""

import logging


def initialize_modules() -> None:
    """
    No-op for eager module initialization.
    Module and GUI component loading is now handled lazily by the lazy loader system.
    This function is kept for compatibility and future use.
    """
    logging.info(
        "Module initialization is now handled lazily. No eager imports performed."
    )


def load_plugins() -> None:
    """Discover and load plugins using the plugin manager."""
    try:
        from app_files.utils.plugin_system import plugin_manager    # pylint: disable=import-outside-toplevel

        # Justification: Lazy import to avoid unnecessary dependency loading at startup
        plugin_manager.discover_plugins()
        plugin_manager.load_plugins()
    except ImportError:
        logging.warning("Plugin system not available")
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Justification: Continue app startup even if plugin loading fails
        logging.error("Error loading plugins: %s", e)
