"""Centralized logging configuration for RickyMama application"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

class LoggerSetup:
    """Centralized logging configuration with file rotation"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSetup, cls).__new__(cls)
        return cls._instance
    
    @staticmethod
    def setup_logger(name: str, config: dict) -> logging.Logger:
        """Setup logger with file and console handlers
        
        Args:
            name: Logger name (usually __name__)
            config: Logging configuration dictionary with keys:
                - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                - file_path: Path to log file
                - max_file_size: Maximum size before rotation (e.g., "10MB")
                - backup_count: Number of backup files to keep
        
        Returns:
            Configured logger instance
        """
        # Check if logger already exists
        if name in LoggerSetup._loggers:
            return LoggerSetup._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.get('level', 'INFO')))
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Ensure log directory exists
        log_file = config.get('file_path', './logs/rickymama.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Parse max file size
        max_size_str = config.get('max_file_size', '10MB')
        max_size = LoggerSetup._parse_size(max_size_str)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=config.get('backup_count', 5)
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Console formatter (simpler)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Store logger reference
        LoggerSetup._loggers[name] = logger
        
        return logger
    
    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Parse size string to bytes
        
        Examples:
            "10MB" -> 10485760
            "5GB" -> 5368709120
            "100KB" -> 102400
        """
        size_str = size_str.strip().upper()
        
        units = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024
        }
        
        # Extract number and unit
        for unit, multiplier in units.items():
            if size_str.endswith(unit):
                try:
                    number = float(size_str[:-len(unit)])
                    return int(number * multiplier)
                except ValueError:
                    pass
        
        # Default to 10MB if parsing fails
        return 10 * 1024 * 1024
    
    @staticmethod
    def get_logger(name: str, config: Optional[dict] = None) -> logging.Logger:
        """Get or create a logger
        
        Args:
            name: Logger name
            config: Optional configuration dict, uses defaults if not provided
        
        Returns:
            Logger instance
        """
        if config is None:
            config = {
                'level': 'INFO',
                'file_path': './logs/rickymama.log',
                'max_file_size': '10MB',
                'backup_count': 5
            }
        
        return LoggerSetup.setup_logger(name, config)
    
    @staticmethod
    def shutdown():
        """Shutdown all loggers and handlers"""
        for logger in LoggerSetup._loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        LoggerSetup._loggers.clear()


class LoggerMixin:
    """Mixin class to add logging capability to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            # Try to get config from self.config or use defaults
            config = None
            if hasattr(self, 'config') and hasattr(self.config, 'get_logging_config'):
                config = self.config.get_logging_config()
            
            self._logger = LoggerSetup.get_logger(
                self.__class__.__module__ + '.' + self.__class__.__name__,
                config
            )
        return self._logger


def get_logger(name: str = None) -> logging.Logger:
    """Convenience function to get a logger
    
    Args:
        name: Logger name, defaults to caller's module name
    
    Returns:
        Logger instance
    """
    if name is None:
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'rickymama')
        else:
            name = 'rickymama'
    
    return LoggerSetup.get_logger(name)