import os
import importlib
import threading
import gc
import time
from functools import lru_cache

def preload_modules(modules):
    """Preload specified modules to optimize startup time."""
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            print(f"Warning: Could not preload module {module}: {e}")

def background_preload(modules):
    """Preload modules in background threads for non-blocking startup."""
    def load_module(module_name):
        try:
            importlib.import_module(module_name)
        except ImportError:
            pass
    
    threads = []
    for module in modules:
        thread = threading.Thread(target=load_module, args=(module,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    return threads

def optimize_memory():
    """Optimize memory settings for better performance."""
    # Disable automatic garbage collection during startup
    gc.disable()
    
    # Set better garbage collection thresholds
    gc.set_threshold(700, 10, 10)
    
    # Re-enable garbage collection after optimization
    def re_enable_gc():
        time.sleep(2)  # Wait for startup to complete
        gc.enable()
    
    gc_thread = threading.Thread(target=re_enable_gc)
    gc_thread.daemon = True
    gc_thread.start()

def setup_environment_variables():
    """Setup optimal environment variables for performance."""
    # Optimize scientific libraries for single-threaded use during startup
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    
    # Optimize matplotlib
    os.environ['MPLBACKEND'] = 'TkAgg'

@lru_cache(maxsize=128)
def cached_import(module_name):
    """Cache imported modules to avoid repeated imports."""
    return importlib.import_module(module_name)

def optimize_imports():
    """Optimize imports by preloading commonly used modules."""
    # Setup environment first
    setup_environment_variables()
    optimize_memory()
    
    # Core modules to load immediately
    core_modules = [
        'tkinter',
        'tkinter.ttk'
    ]
    
    # Heavy modules to load in background
    heavy_modules = [
        'numpy',
        'scipy',
        'matplotlib.pyplot',
        'sympy',
        'matplotlib.backends.backend_tkagg'
    ]
    
    # Load core modules synchronously
    print("Loading core modules...")
    preload_modules(core_modules)
    
    # Load heavy modules in background
    print("Preloading heavy modules in background...")
    background_threads = background_preload(heavy_modules)
    
    return background_threads

def measure_startup_time():
    """Measure and report startup optimization performance."""
    start_time = time.time()
    threads = optimize_imports()
    end_time = time.time()
    
    print(f"Core startup completed in {end_time - start_time:.2f} seconds")
    print(f"Background loading started for {len(threads)} modules")

if __name__ == "__main__":
    measure_startup_time()
