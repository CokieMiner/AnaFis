# -*- coding: utf-8 -*-
"""
Runtime hook for optimizing AnaFis startup performance.
This runs before the main application starts.
"""

import threading
import sys
import gc
import os
from typing import List

def background_import(module_name: str) -> None:
    """Import a module in the background without blocking main thread."""
    try:
        __import__(module_name)
    except (ImportError, Exception):
        # Module import failed - continue silently
        return

def optimize_memory() -> None:
    """Optimize memory settings for better performance."""
    # Disable automatic garbage collection during startup
    gc.disable()
    
    # Set garbage collection thresholds for better performance
    # (threshold0, threshold1, threshold2)
    gc.set_threshold(700, 10, 10)

def preload_heavy_modules() -> None:
    """Preload heavy modules in background threads."""
    # Use a safer approach than setting an attribute directly on sys module
    # Check if we've already started preloading to avoid duplicate threads
    preload_flag_name = '_anafis_preloading'
    
    # Use getattr with a default value to safely check if attribute exists
    if not getattr(sys, preload_flag_name, False):
        # Set the flag using setattr to avoid direct attribute access warning
        setattr(sys, preload_flag_name, True)
        
        # Modules to preload in background
        heavy_modules: List[str] = [
            'numpy.core',
            'numpy.linalg',
            'scipy.special',
            'scipy.optimize',
            'scipy.integrate',
            'matplotlib.backends.backend_tkagg',
            'matplotlib.figure',
            'matplotlib.pyplot',
            'sympy.core',
            'sympy.parsing'
        ]
        
        # Start background threads for heavy modules
        for module in heavy_modules:
            thread = threading.Thread(target=background_import, args=(module,))
            thread.daemon = True
            thread.start()

def setup_environment() -> None:
    """Setup optimal environment variables for performance."""
    # Optimize NumPy for single-threaded use (faster startup)
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    
    # Disable matplotlib's font cache during startup
    os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), '.matplotlib_cache')

# Execute optimizations
optimize_memory()
setup_environment()
preload_heavy_modules()
