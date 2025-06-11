"""
Lazy loading system for AnaFis application.
This module provides lazy loading capabilities to improve startup performance
by deferring the import of heavy modules until they are actually needed.
"""

import importlib
import threading
import logging
from typing import Any, Dict, Optional, Set
from types import ModuleType

class LazyModule:
    """A proxy object that loads a module on first access"""
    
    def __init__(self, module_name: str, attribute: Optional[str] = None):
        self._module_name = module_name
        self._attribute = attribute
        self._module: Optional[ModuleType] = None
        self._loading = False
        self._lock = threading.Lock()
    
    def _load_module(self) -> ModuleType:
        """Load the actual module"""
        if self._module is not None:
            return self._module
            
        with self._lock:
            if self._module is not None:
                return self._module
                
            if self._loading:
                # Avoid circular loading
                raise ImportError(f"Circular import detected for {self._module_name}")
                
            self._loading = True
            try:
                self._module = importlib.import_module(self._module_name)
                logging.debug(f"Lazy loaded module: {self._module_name}")
                return self._module
            except ImportError as e:
                logging.error(f"Failed to lazy load {self._module_name}: {e}")
                raise
            finally:
                self._loading = False
    
    def __getattr__(self, name: str) -> Any:
        """Get an attribute from the loaded module"""
        module = self._load_module()
        if self._attribute:        # If we're proxying a specific attribute, get it first
            attr = getattr(module, self._attribute)
            return getattr(attr, name)
        return getattr(module, name)
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Make the proxy callable if the target is callable"""
        module = self._load_module()
        if self._attribute:
            attr = getattr(module, self._attribute)
            if not callable(attr):
                raise TypeError(f"'{self._attribute}' object is not callable")
            return attr(*args, **kwargs)
        
        # Check if the module itself is callable (rare case)
        if hasattr(module, '__call__'):
            return module(*args, **kwargs)  # type: ignore
        else:
            raise TypeError(f"Module '{self._module_name}' is not callable")
    
    def __repr__(self) -> str:
        if self._module is not None:
            return f"<LazyModule {self._module_name} (loaded)>"
        return f"<LazyModule {self._module_name} (not loaded)>"

class ModuleCache:
    """Cache for loaded modules to avoid repeated imports"""
    
    def __init__(self):
        self._cache: Dict[str, ModuleType] = {}
        self._lock = threading.Lock()
    
    def get(self, module_name: str) -> Optional[ModuleType]:
        """Get a cached module"""
        with self._lock:
            return self._cache.get(module_name)
    
    def put(self, module_name: str, module: ModuleType) -> None:
        """Cache a module"""
        with self._lock:
            self._cache[module_name] = module
    
    def clear(self) -> None:
        """Clear the cache"""
        with self._lock:
            self._cache.clear()

class LazyLoader:
    """Main lazy loading manager"""
    
    def __init__(self):
        self.cache = ModuleCache()
        self.registered_modules: Set[str] = set()
        self.preloaded_modules: Set[str] = set()
        self._lock = threading.Lock()
    
    def register_lazy_module(self, module_name: str, alias: Optional[str] = None) -> LazyModule:
        """Register a module for lazy loading"""
        with self._lock:
            self.registered_modules.add(module_name)
        
        # Check if already cached
        cached = self.cache.get(module_name)
        if cached:
            return LazyModule(module_name)
        
        return LazyModule(module_name)
    
    def preload_module(self, module_name: str) -> bool:
        """Preload a module in the background"""
        if module_name in self.preloaded_modules:
            return True
            
        try:
            module = importlib.import_module(module_name)
            self.cache.put(module_name, module)
            with self._lock:
                self.preloaded_modules.add(module_name)
            logging.debug(f"Preloaded module: {module_name}")
            return True
        except ImportError as e:
            logging.warning(f"Failed to preload {module_name}: {e}")
            return False
    
    def get_registered_modules(self) -> Set[str]:
        """Get list of registered modules"""
        with self._lock:
            return self.registered_modules.copy()
    
    def get_preloaded_modules(self) -> Set[str]:
        """Get list of preloaded modules"""
        with self._lock:
            return self.preloaded_modules.copy()
    
    def clear_cache(self) -> None:
        """Clear all caches"""
        self.cache.clear()
        with self._lock:
            self.preloaded_modules.clear()

# Global lazy loader instance
lazy_loader = LazyLoader()

def lazy_import(module_name: str, attribute: Optional[str] = None) -> LazyModule:
    """Convenience function for lazy importing"""
    if attribute:
        return LazyModule(module_name, attribute)
    return lazy_loader.register_lazy_module(module_name)
