"""Feature flags manager for AnaFis application"""
from typing import Dict, Set


class FeatureManager:
    """Manages feature flags for the application"""
    
    def __init__(self):
        self._features: Dict[str, bool] = {
            'curve_fitting': True,
            'uncertainty_calculator': True,
            'advanced_plotting': True,
            'data_export': True,
            'plugin_system': True,
        }
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the feature manager"""
        if self._initialized:
            return
            
        # Load feature settings from user preferences
        try:
            from .user_preferences import user_preferences
            saved_features = user_preferences.get_preference('enabled_features', {})
            self._features.update(saved_features)
        except ImportError:
            pass
        
        self._initialized = True
    
    def is_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self._features.get(feature, False)
    
    def enable_feature(self, feature: str) -> None:
        """Enable a feature"""
        self._features[feature] = True
    
    def disable_feature(self, feature: str) -> None:
        """Disable a feature"""
        self._features[feature] = False
    
    def get_enabled_features(self) -> Set[str]:
        """Get all enabled features"""
        return {feature for feature, enabled in self._features.items() if enabled}


# Global feature manager instance
feature_manager = FeatureManager()
