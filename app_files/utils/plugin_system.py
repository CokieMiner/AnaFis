"""Plugin system for AnaFis application"""
import logging
from typing import List, Dict, Any
from pathlib import Path


class PluginManager:
    """Manages plugins for the application"""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.plugin_paths: List[Path] = []
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the plugin manager"""
        if self._initialized:
            return
        
        # Add default plugin directories
        app_dir = Path(__file__).parent.parent.parent
        plugin_dir = app_dir / "plugins"
        if plugin_dir.exists():
            self.plugin_paths.append(plugin_dir)
        
        self._initialized = True
    
    def discover_plugins(self) -> None:
        """Discover available plugins"""
        if not self._initialized:
            self.initialize()
        
        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue
                
            for item in plugin_path.iterdir():
                if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                    plugin_name = item.stem
                    logging.info(f"Discovered plugin: {plugin_name}")
    
    def load_plugins(self) -> None:
        """Load discovered plugins"""
        if not self._initialized:
            self.initialize()
        
        # For now, just log that plugin loading is complete
        # In a real implementation, this would actually load plugin files
        logging.info("Plugin loading completed")
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names"""
        return list(self.plugins.keys())


# Global plugin manager instance
plugin_manager = PluginManager()
