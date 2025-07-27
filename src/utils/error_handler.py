"""Centralized error handling and logging for RickyMama application"""

import logging
import traceback
from typing import Optional, Any, Callable
from functools import wraps
from datetime import datetime

class RickyMamaError(Exception):
    """Base exception class for RickyMama application"""
    pass

class ValidationError(RickyMamaError):
    """Raised when input validation fails"""
    pass

class ParseError(RickyMamaError):
    """Raised when input parsing fails"""
    pass

class DatabaseError(RickyMamaError):
    """Raised when database operations fail"""
    pass

class ConfigurationError(RickyMamaError):
    """Raised when configuration is invalid"""
    pass

class ExportError(RickyMamaError):
    """Raised when export operations fail"""
    pass

class GUIError(RickyMamaError):
    """Raised when GUI operations fail"""
    pass

class CalculationError(RickyMamaError):
    """Raised when business calculations fail"""
    pass

class ProcessingError(RickyMamaError):
    """Raised when data processing fails"""
    pass

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        if logger is None:
            from .logger import get_logger
            logger = get_logger(__name__)
        self.logger = logger
        self.error_log = []
        self.max_error_log_size = 100
    
    def handle_parsing_error(self, line: str, error: Exception) -> str:
        """Handle parsing errors with user-friendly messages"""
        error_msg = f"Failed to parse input: '{line}'"
        
        if isinstance(error, ValidationError):
            error_msg += f"\nValidation Error: {str(error)}"
        elif isinstance(error, ParseError):
            error_msg += f"\nParse Error: {str(error)}"
        else:
            error_msg += f"\nUnexpected Error: {str(error)}"
        
        self.logger.error(error_msg)
        self.log_error('parsing', error_msg, {'line': line, 'error': str(error)})
        
        return error_msg
    
    def handle_database_error(self, operation: str, error: Exception) -> str:
        """Handle database errors with recovery suggestions"""
        error_msg = f"Database operation '{operation}' failed"
        
        if "locked" in str(error).lower():
            error_msg += "\nDatabase is locked. Please try again in a moment."
        elif "constraint" in str(error).lower():
            error_msg += "\nData constraint violation. Please check your input."
        elif "foreign key" in str(error).lower():
            error_msg += "\nRelated data dependency error. Please verify references."
        else:
            error_msg += f"\nError: {str(error)}"
        
        self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
        self.log_error('database', error_msg, {'operation': operation, 'error': str(error)})
        
        return error_msg
    
    def handle_gui_error(self, component: str, error: Exception) -> str:
        """Handle GUI errors with component context"""
        error_msg = f"GUI component '{component}' encountered an error"
        
        if "viewport" in str(error).lower():
            error_msg += "\nDisplay error. Please check your display settings."
        elif "render" in str(error).lower():
            error_msg += "\nRendering error. Try restarting the application."
        else:
            error_msg += f"\nError: {str(error)}"
        
        self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
        self.log_error('gui', error_msg, {'component': component, 'error': str(error)})
        
        return error_msg
    
    def handle_export_error(self, export_type: str, error: Exception) -> str:
        """Handle export errors with file context"""
        error_msg = f"Export operation '{export_type}' failed"
        
        if "permission" in str(error).lower():
            error_msg += "\nFile permission denied. Please check write permissions."
        elif "space" in str(error).lower():
            error_msg += "\nInsufficient disk space. Please free up some space."
        elif "exists" in str(error).lower():
            error_msg += "\nFile already exists. Please choose a different name."
        else:
            error_msg += f"\nError: {str(error)}"
        
        self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
        self.log_error('export', error_msg, {'export_type': export_type, 'error': str(error)})
        
        return error_msg
    
    def show_user_error(self, message: str, details: str = None, error_type: str = "Error"):
        """Display error to user (to be overridden by GUI implementation)"""
        full_message = f"{error_type}: {message}"
        if details:
            full_message += f"\n\nDetails: {details}"
        
        self.logger.error(f"User Error: {full_message}")
        print(full_message)  # Console fallback
    
    def log_error(self, category: str, message: str, context: dict = None):
        """Log error for later analysis"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'message': message,
            'context': context or {}
        }
        
        self.error_log.append(error_entry)
        
        # Limit error log size
        if len(self.error_log) > self.max_error_log_size:
            self.error_log = self.error_log[-self.max_error_log_size:]
    
    def get_error_summary(self) -> dict:
        """Get summary of recent errors"""
        if not self.error_log:
            return {'total': 0, 'by_category': {}}
        
        summary = {
            'total': len(self.error_log),
            'by_category': {},
            'recent': self.error_log[-10:]  # Last 10 errors
        }
        
        for error in self.error_log:
            category = error['category']
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
        
        return summary
    
    def clear_error_log(self):
        """Clear the error log"""
        self.error_log.clear()
        self.logger.info("Error log cleared")


def error_handler(error_type: type = Exception, 
                 handler_func: Optional[Callable] = None,
                 default_return: Any = None,
                 reraise: bool = False):
    """Decorator for automatic error handling
    
    Args:
        error_type: Type of exception to catch
        handler_func: Optional custom handler function
        default_return: Default value to return on error
        reraise: Whether to re-raise the exception after handling
    
    Example:
        @error_handler(ValidationError, default_return=[])
        def parse_input(text):
            # parsing logic
            return parsed_data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                # Get logger
                from .logger import get_logger
                logger = get_logger(func.__module__)
                
                # Log the error
                logger.error(f"Error in {func.__name__}: {str(e)}")
                
                # Call custom handler if provided
                if handler_func:
                    result = handler_func(e, *args, **kwargs)
                    if result is not None:
                        return result
                
                # Re-raise if requested
                if reraise:
                    raise
                
                # Return default value
                return default_return
        
        return wrapper
    return decorator


class ErrorContext:
    """Context manager for error handling blocks"""
    
    def __init__(self, operation: str, error_handler: ErrorHandler = None):
        self.operation = operation
        self.error_handler = error_handler or ErrorHandler()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Handle the error
            if issubclass(exc_type, ParseError):
                self.error_handler.handle_parsing_error(self.operation, exc_val)
            elif issubclass(exc_type, DatabaseError):
                self.error_handler.handle_database_error(self.operation, exc_val)
            elif issubclass(exc_type, GUIError):
                self.error_handler.handle_gui_error(self.operation, exc_val)
            elif issubclass(exc_type, ExportError):
                self.error_handler.handle_export_error(self.operation, exc_val)
            else:
                # Generic error handling
                self.error_handler.logger.error(
                    f"Unexpected error in {self.operation}: {exc_val}\n{traceback.format_exc()}"
                )
            
            # Don't suppress the exception by default
            return False


# Global error handler instance
_global_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler

def set_error_handler(handler: ErrorHandler):
    """Set global error handler instance"""
    global _global_error_handler
    _global_error_handler = handler