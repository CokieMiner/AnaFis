"""
Enhanced lazy loading system for AnaFis application.
This module provides advanced lazy loading capabilities to improve startup performance
by deferring the import of heavy modules until they are actually needed.
"""

import importlib
import threading
import logging
import time
from typing import Any, Dict, Optional, Set, List, Callable, Tuple, cast
from types import ModuleType
from dataclasses import dataclass
from enum import Enum


class LoadStatus(Enum):
    """Status of module loading"""

    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"


@dataclass
class ModuleInfo:
    """Information about a module"""

    name: str
    status: LoadStatus
    load_time: Optional[float] = None
    error: Optional[str] = None
    dependencies: Optional[Set[str]] = None
    size_estimate: Optional[int] = None


class LazyModule:
    """A proxy object that loads a module on first access with enhanced features"""

    def __init__(
        self,
        module_name: str,
        attribute: Optional[str] = None,
        preload_priority: int = 0,
        dependencies: Optional[List[str]] = None,
    ):
        self._module_name = module_name
        self._attribute = attribute
        self._module: Optional[ModuleType] = None
        self._loading = False
        self.lock = threading.Lock()
        self._preload_priority = preload_priority
        self._dependencies = set(dependencies or [])
        self._load_start_time: Optional[float] = None

    def _load_module(self) -> ModuleType:
        """Load the actual module with enhanced error handling and timing"""
        if self._module is not None:
            return self._module

        with self.lock:
            if self._module is not None:
                return self._module

            if self._loading:
                # Avoid circular loading
                raise ImportError(f"Circular import detected for {self._module_name}")

            self._loading = True
            self._load_start_time = time.time()

            try:
                # Load dependencies first if specified
                for dep in self._dependencies:
                    try:
                        importlib.import_module(dep)
                        logging.debug("Loaded dependency: %s", dep)
                    except ImportError as e:
                        logging.warning("Failed to load dependency %s: %s", dep, e)

                # Load the main module
                self._module = importlib.import_module(self._module_name)
                load_time = time.time() - self._load_start_time

                # Update lazy loader statistics
                lazy_loader.record_module_load(self._module_name, load_time, None)

                logging.debug(
                    "Lazy loaded module: %s in %.3fs", self._module_name, load_time
                )
                return self._module

            except ImportError as e:
                load_time = time.time() - self._load_start_time
                lazy_loader.record_module_load(self._module_name, load_time, str(e))
                logging.error("Failed to lazy load %s: %s", self._module_name, e)
                raise
            finally:
                self._loading = False

    def __getattr__(self, name: str) -> Any:
        """Get an attribute from the loaded module"""
        module = self._load_module()
        if self._attribute:
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
        if hasattr(module, "__call__"):
            return cast(Callable[..., Any], module)(*args, **kwargs)
        else:
            raise TypeError(f"Module '{self._module_name}' is not callable")

    def __repr__(self) -> str:
        if self._module is not None:
            return f"<LazyModule {self._module_name} (loaded)>"
        return f"<LazyModule {self._module_name} (not loaded)>"

    @property
    def is_loaded(self) -> bool:
        """Check if the module is loaded"""
        return self._module is not None

    @property
    def load_priority(self) -> int:
        """Get the preload priority"""
        return self._preload_priority


class ModuleCache:
    """Enhanced cache for loaded modules with statistics"""

    def __init__(self):
        self._cache: Dict[str, ModuleType] = {}
        self.lock = threading.Lock()
        self._access_count: Dict[str, int] = {}
        self._last_access: Dict[str, float] = {}

    def get(self, module_name: str) -> Optional[ModuleType]:
        """Get a cached module and update access statistics"""
        with self.lock:
            module = self._cache.get(module_name)
            if module:
                self._access_count[module_name] = (
                    self._access_count.get(module_name, 0) + 1
                )
                self._last_access[module_name] = time.time()
            return module

    def put(self, module_name: str, module: ModuleType) -> None:
        """Cache a module"""
        with self.lock:
            self._cache[module_name] = module
            self._access_count[module_name] = 1
            self._last_access[module_name] = time.time()

    def clear(self) -> None:
        """Clear the cache"""
        with self.lock:
            self._cache.clear()
            self._access_count.clear()
            self._last_access.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "cached_modules": len(self._cache),
                "most_accessed": sorted(
                    self._access_count.items(), key=lambda x: x[1], reverse=True
                )[:5],
                "recently_accessed": sorted(
                    self._last_access.items(), key=lambda x: x[1], reverse=True
                )[:5],
            }


class LazyLoader:
    """Enhanced lazy loading manager with performance monitoring"""

    def __init__(self):
        self.cache = ModuleCache()
        self.registered_modules: Dict[str, LazyModule] = {}
        self.attribute_proxies: Dict[Tuple[str, Optional[str]], LazyModule] = {}
        self.preloaded_modules: Set[str] = set()
        self.module_stats: Dict[str, ModuleInfo] = {}
        self.lock = threading.Lock()
        self._preload_queue: List[Tuple[str, int]] = []  # (module_name, priority)
        self._background_thread: Optional[threading.Thread] = None

    def register_lazy_module(
        self,
        module_name: str,
        alias: Optional[str] = None,
        preload_priority: int = 0,
        dependencies: Optional[List[str]] = None,
    ) -> LazyModule:
        """Register a module for lazy loading with priority and dependencies"""
        with self.lock:
            # Check if already cached
            cached = self.cache.get(module_name)
            if cached:
                return LazyModule(module_name)

            # Create new lazy module
            lazy_module = LazyModule(module_name, alias, preload_priority, dependencies)
            self.registered_modules[module_name] = lazy_module

            # Add to preload queue if priority > 0
            if preload_priority > 0:
                self._preload_queue.append((module_name, preload_priority))
                self._preload_queue.sort(key=lambda x: x[1], reverse=True)

            # Initialize module info
            self.module_stats[module_name] = ModuleInfo(
                name=module_name,
                status=LoadStatus.NOT_LOADED,
                dependencies=set(dependencies) if dependencies else set(),
            )

            return lazy_module

    def preload_module(self, module_name: str) -> bool:
        """Preload a module in the background with enhanced error handling"""
        if module_name in self.preloaded_modules:
            return True

        start_time = time.time()
        try:
            # Update status to loading
            if module_name in self.module_stats:
                self.module_stats[module_name].status = LoadStatus.LOADING

            module = importlib.import_module(module_name)
            load_time = time.time() - start_time

            self.cache.put(module_name, module)
            with self.lock:
                self.preloaded_modules.add(module_name)

            # Update statistics
            self.record_module_load(module_name, load_time, None)

            logging.debug("Preloaded module: %s in %.3fs", module_name, load_time)
            return True

        except ImportError as e:
            load_time = time.time() - start_time
            self.record_module_load(module_name, load_time, str(e))
            logging.warning("Failed to preload %s: %s", module_name, e)
            return False

    def start_background_preloading(self) -> None:
        """Start background preloading of high-priority modules"""
        if self._background_thread and self._background_thread.is_alive():
            return

        def preload_worker() -> None:
            """Background worker for preloading modules"""
            for module_name, _ in self._preload_queue:
                if module_name not in self.preloaded_modules:
                    try:
                        self.preload_module(module_name)
                        time.sleep(0.1)  # Small delay to avoid blocking
                    except ImportError as e:
                        logging.error(
                            "Background preload failed for %s: %s", module_name, e
                        )

        self._background_thread = threading.Thread(target=preload_worker, daemon=True)
        self._background_thread.start()
        logging.info("Background preloading started")

    def record_module_load(
        self, module_name: str, load_time: float, error: Optional[str]
    ) -> None:
        """Record module loading statistics"""
        with self.lock:
            if module_name in self.module_stats:
                info = self.module_stats[module_name]
                info.load_time = load_time
                info.status = LoadStatus.FAILED if error else LoadStatus.LOADED
                info.error = error

    def get_loading_stats(self) -> Dict[str, Any]:
        """Get comprehensive loading statistics"""
        with self.lock:
            total_modules = len(self.module_stats)
            loaded_modules = sum(
                1
                for info in self.module_stats.values()
                if info.status == LoadStatus.LOADED
            )
            failed_modules = sum(
                1
                for info in self.module_stats.values()
                if info.status == LoadStatus.FAILED
            )

            avg_load_time = 0.0
            if loaded_modules > 0:
                load_times = [
                    info.load_time
                    for info in self.module_stats.values()
                    if info.load_time is not None
                ]
                avg_load_time = sum(load_times) / len(load_times) if load_times else 0.0

            return {
                "total_modules": total_modules,
                "loaded_modules": loaded_modules,
                "failed_modules": failed_modules,
                "preloaded_modules": len(self.preloaded_modules),
                "average_load_time": avg_load_time,
                "cache_stats": self.cache.get_stats(),
                "module_details": {
                    name: {
                        "status": info.status.value,
                        "load_time": info.load_time,
                        "error": info.error,
                        "dependencies": (
                            list(info.dependencies) if info.dependencies else []
                        ),
                    }
                    for name, info in self.module_stats.items()
                },
            }

    def clear_cache(self) -> None:
        """Clear all caches"""
        self.cache.clear()
        with self.lock:
            self.preloaded_modules.clear()
            self.module_stats.clear()


# Global lazy loader instance
lazy_loader = LazyLoader()


def lazy_import(
    module_name: str,
    attribute: Optional[str] = None,
    preload_priority: int = 0,
    dependencies: Optional[List[str]] = None,
) -> LazyModule:
    """Convenience function for lazy importing with enhanced options (singleton proxies)"""
    key = (module_name, attribute)
    with lazy_loader.lock:
        if key in lazy_loader.attribute_proxies:
            return lazy_loader.attribute_proxies[key]
        if attribute:
            proxy = LazyModule(module_name, attribute, preload_priority, dependencies)
            lazy_loader.attribute_proxies[key] = proxy
            return proxy
        proxy = lazy_loader.register_lazy_module(
            module_name, preload_priority=preload_priority, dependencies=dependencies
        )
        lazy_loader.attribute_proxies[key] = proxy
        return proxy


def start_background_preloading() -> None:
    """Start background preloading of modules"""
    lazy_loader.start_background_preloading()


def get_loading_statistics() -> Dict[str, Any]:
    """Get comprehensive loading statistics"""
    return lazy_loader.get_loading_stats()
