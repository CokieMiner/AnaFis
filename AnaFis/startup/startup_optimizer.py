"""
Startup optimization utilities for AnaFis.
Sets up environment variables and memory optimizations for fast startup and lazy loading.
"""

import os
import importlib
import threading
import gc
import time
from functools import lru_cache
from typing import List, Any
import logging


def preload_modules(modules: List[str]) -> None:
    """Preload specified modules to optimize startup time."""
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            logging.warning("Could not preload module %s: %s", module, e)


def optimize_memory() -> None:
    """Optimize memory settings for better performance."""
    gc.disable()
    gc.set_threshold(700, 10, 10)

    def re_enable_gc() -> None:
        time.sleep(2)
        gc.enable()

    gc_thread = threading.Thread(target=re_enable_gc)
    gc_thread.daemon = True
    gc_thread.start()


def setup_environment_variables() -> None:
    """Setup optimal environment variables for performance."""
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["MPLBACKEND"] = "TkAgg"


def optimize_imports() -> None:
    """Optimize imports by setting up environment and avoiding heavy preloading."""
    setup_environment_variables()
    optimize_memory()
    core_modules: List[str] = ["tkinter", "tkinter.ttk"]
    logging.info("Loading core modules...")
    preload_modules(core_modules)
    logging.info("Heavy modules will be loaded on-demand via lazy loading.")


def measure_startup_time() -> None:
    """Measure and report startup optimization performance with lazy loading."""
    start_time = time.time()
    optimize_imports()
    end_time = time.time()
    logging.info("Core startup completed in %.2f seconds", end_time - start_time)
    logging.info("Lazy loading enabled - heavy modules will load on demand.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    measure_startup_time()
