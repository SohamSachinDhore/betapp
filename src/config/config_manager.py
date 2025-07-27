"""Configuration management for RickyMama application"""

import json
import os
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """Application configuration management with nested key support"""
    
    DEFAULT_CONFIG = {
        "database": {
            "path": "./data/rickymama.db",
            "backup_interval": 86400,
            "max_connections": 5
        },
        "gui": {
            "window_width": 1200,
            "window_height": 800,
            "theme": "default",
            "auto_save_interval": 300
        },
        "export": {
            "default_path": "./exports/",
            "auto_backup": True,
            "max_export_rows": 100000
        },
        "validation": {
            "strict_pana_validation": True,
            "max_input_lines": 1000,
            "timeout_seconds": 30
        },
        "logging": {
            "level": "INFO",
            "file_path": "./logs/rickymama.log",
            "max_file_size": "10MB",
            "backup_count": 5
        }
    }
    
    def __init__(self, config_path: str = "./config/settings.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except Exception as e:
                self.logger.error(f"Failed to load config from {self.config_path}: {e}")
                self.logger.info("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            self.logger.info(f"Config file not found at {self.config_path}, using defaults")
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            # Save default config
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults (deep merge)"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config to {self.config_path}: {e}")
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value with dot notation support
        
        Examples:
            config.get('database.path')
            config.get('gui.window_width')
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = True):
        """Set configuration value with dot notation support"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Optionally save to file
        if save:
            self.save_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self.load_config()
        self.logger.info("Configuration reloaded")
    
    def reset_to_defaults(self, save: bool = True):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        if save:
            self.save_config()
        self.logger.info("Configuration reset to defaults")
    
    def validate_config(self) -> bool:
        """Validate configuration values"""
        try:
            # Validate database path
            db_path = self.get('database.path')
            if not db_path:
                self.logger.error("Database path not configured")
                return False
            
            # Validate window dimensions
            width = self.get('gui.window_width')
            height = self.get('gui.window_height')
            if width < 800 or height < 600:
                self.logger.warning("Window dimensions too small, using minimum values")
                self.set('gui.window_width', max(800, width), save=False)
                self.set('gui.window_height', max(600, height), save=False)
            
            # Validate export path
            export_path = self.get('export.default_path')
            if not export_path:
                self.logger.error("Export path not configured")
                return False
            
            # Validate logging level
            log_level = self.get('logging.level')
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if log_level not in valid_levels:
                self.logger.warning(f"Invalid log level {log_level}, using INFO")
                self.set('logging.level', 'INFO', save=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration section"""
        return self.get_section('database')
    
    def get_gui_config(self) -> Dict[str, Any]:
        """Get GUI configuration section"""
        return self.get_section('gui')
    
    def get_export_config(self) -> Dict[str, Any]:
        """Get export configuration section"""
        return self.get_section('export')
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration section"""
        return self.get_section('validation')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration section"""
        return self.get_section('logging')
    
    def __repr__(self):
        return f"ConfigManager(config_path='{self.config_path}')"


def create_config_manager(config_path: str = "./config/settings.json") -> ConfigManager:
    """Factory function to create config manager"""
    return ConfigManager(config_path)