import os
import importlib
import threading
import gc
import time
from functools import lru_cache
from typing import List, Any

def preload_modules(modules: List[str]) -> None:
    """Preload specified modules to optimize startup time."""
    for module in modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            print(f"Warning: Could not preload module {module}: {e}")

def background_preload(modules: List[str]) -> List[threading.Thread]:
    """Preload modules in background threads for non-blocking startup."""
    def load_module(module_name: str) -> None:
        try:
            importlib.import_module(module_name)
        except ImportError:
            # Module not available for preloading - silently continue
            return
    
    threads: List[threading.Thread] = []
    for module in modules:
        thread = threading.Thread(target=load_module, args=(module,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    return threads

def optimize_memory() -> None:
    """Optimize memory settings for better performance."""
    # Disable automatic garbage collection during startup
    gc.disable()
    
    # Set better garbage collection thresholds
    gc.set_threshold(700, 10, 10)
    
    # Re-enable garbage collection after optimization
    def re_enable_gc() -> None:
        time.sleep(2)  # Wait for startup to complete
        gc.enable()
    
    gc_thread = threading.Thread(target=re_enable_gc)
    gc_thread.daemon = True
    gc_thread.start()

def setup_environment_variables() -> None:
    """Setup optimal environment variables for performance."""
    # Optimize scientific libraries for single-threaded use during startup
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    
    # Optimize matplotlib
    os.environ['MPLBACKEND'] = 'TkAgg'

@lru_cache(maxsize=128)
def cached_import(module_name: str) -> Any:
    """Cache imported modules to avoid repeated imports."""
    return importlib.import_module(module_name)

def optimize_imports() -> List[threading.Thread]:
    """Optimize imports by setting up environment and avoiding heavy preloading (lazy loading compatible)."""
    # Setup environment first
    setup_environment_variables()
    optimize_memory()
    
    # Core modules to load immediately (lightweight only)
    core_modules: List[str] = [
        'tkinter',
        'tkinter.ttk'
    ]
    
    # Note: Heavy modules are now lazy-loaded on demand
    # No longer preloading numpy, scipy, matplotlib, sympy as they're lazy-loaded
    
    # Load core modules synchronously
    print("Loading core modules...")
    preload_modules(core_modules)
    
    # Instead of preloading heavy modules, just set up the environment
    print("Preloading heavy modules in background...")
    print("Note: Heavy modules will be loaded on-demand via lazy loading")
    
    # Return empty list since we're not doing background loading anymore
    return []

def measure_startup_time() -> None:
    """Measure and report startup optimization performance with lazy loading."""
    start_time = time.time()
    threads = optimize_imports()
    end_time = time.time()
    
    print(f"Core startup completed in {end_time - start_time:.2f} seconds")
    print(f"Lazy loading enabled - heavy modules will load on demand")
    if threads:
        print(f"Background threads started: {len(threads)}")
    else:
        print("No background loading - using lazy loading instead")

if __name__ == "__main__":
    measure_startup_time()
