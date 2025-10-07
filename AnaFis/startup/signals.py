"""Signal handling and startup optimizations for AnaFis."""

import gc
import logging
import os
import signal
import threading
from typing import Any


def handle_signal(signum: int, _frame: Any) -> None:
    """Handle termination signals and exit the application immediately."""
    logging.info("Received signal %s, terminating application...", signum)
    os._exit(0)


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful application termination."""
    try:
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, handle_signal)
    except OSError as e:
        logging.debug("Could not setup signal handlers: %s", e)


def apply_startup_optimizations() -> None:
    """Apply startup optimizations such as import optimization and temporary GC disabling."""
    try:
        from startup.startup_optimizer import (
            optimize_imports,
        )  # pylint: disable=import-outside-toplevel

        optimize_imports()
    except ImportError as e:
        logging.warning(
            "Could not import startup optimizer: %s. Applying fallback GC optimization.",
            e,
        )
        gc.disable()
        threading.Timer(3.0, gc.enable).start()
