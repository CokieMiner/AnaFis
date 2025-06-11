# -*- coding: utf-8 -*-
"""
Runtime hook for optimizing AnaFis startup performance.
This runs before the main application starts.
"""

import threading
import sys
import gc
import os

def background_import(module_name):
    """Import a module in the background without blocking main thread."""
    try:
        __import__(module_name)
    except ImportError:
        pass
    except Exception:
        pass

def optimize_memory():
    """Optimize memory settings for better performance."""
    # Disable automatic garbage collection during startup
    gc.disable()
    
    # Set garbage collection thresholds for better performance
    # (threshold0, threshold1, threshold2)
    gc.set_threshold(700, 10, 10)

def preload_heavy_modules():
    """Preload heavy modules in background threads."""
    if not hasattr(sys, '_anafis_preloading'):
        sys._anafis_preloading = True
        
        # Modules to preload in background
        heavy_modules = [
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

def setup_environment():
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
